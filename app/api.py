import os

from flask import Flask, jsonify, Response, request
from flask.views import MethodView
from flasgger import Swagger

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    JWTManager
)

from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config import APP_VERSION, JWT_SECRET_KEY, logger
from dependencies import Session
from authentication import check_password
from errors import HttpError
from functions.functions_main import check_extension_file
from functions.functions_loginmetric import add_login_metric
from functions.functions_collection import (
    get_collection_user_by_id,
    add_document_to_collection,
    delete_collection,
    delete_document_from_collection,
    add_collection
)
from models import (
    LoginMetric,
    User,
    Document,
    DocumentCollectionAssociation,
    Collection
)
from schemas import (
    validate,
    UserSchema,
    UserGetSchemaResponse,
    UpdateUserSchema,
    DocumentSchemaResponse,
    UpdateDocumentSchemaRequest,
    CollectionListSchemaResponse,
    CollectionGetSchemaResponse,
    CollectionCreateSchemaRequest
)
from functions.functions_document import (
    get_document_user_by_id,
    calculate_tf_idf_for_document,
    process_text,
    add_document,
    reading_file,
    update_document,
    delete_document
)
from functions.functions_user import (
    get_user_by_email,
    add_user,
    get_user_by_id,
    update_user
)

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime, time, timedelta


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["SWAGGER"] = {"openapi": "3.0.0"}
API_VERSION_URL_PREFIX_V1 = f"/api/v1"

swagger = Swagger(app, template_file="doc_api.yml")
jwt = JWTManager(app)

@app.errorhandler(HttpError)
def error_headler(err: HttpError):

    # Функция для формирования ответа на ошибку
    http_responce = jsonify({"error": err.message})
    http_responce.status_code = err.status_code
    logger.error(f"Ошибка {err.status_code}: {err.message}")
    return http_responce


@app.before_request
def before_request():
    request.db_session = Session()


@app.after_request
def after_request(reponse: Response):
    request.db_session.close()
    return reponse


class BaseView(MethodView):
    """
    Базовый класс для обработки общих функций
    """

    @property
    def user_id(self):
        return int(get_jwt_identity())

    def handle_validation_errors(self, error_validation_data):
        # Обработка ошибок валидации
        raise HttpError(
            400,
            f"{error_validation_data[0]["loc"][0]}: {error_validation_data[0]["msg"]}"
        )
    
    def handle_error(
        self,
        error: type(Exception),
        message: str,
        status_code: int
    ) -> HttpError:
        raise HttpError(status_code, message)
        


class StatusView(MethodView):
    """
    Класс для проверки статуса API
    """

    def get(self):
        return jsonify({"status": "OK"})


class MetricsView(MethodView):
    """
    Класс для получения метрик
    """

    @jwt_required()
    def get(self):

        # Получаем дату и время начала дня
        start_of_day = datetime.combine(datetime.now().date(), time.min)

        # Возвращаем количество зарегистрированных пользователей
        count_reg_users = request.db_session.query(User).count()

        # Возвращаем количество пользователей вернувшихся на сайт
        count_return_users = request.db_session.query(func.count(
            LoginMetric.user_id.distinct()
        )).scalar()

        # Возвращаем количество пользователей вернувшихся на сайт сегодня
        count_return_users_today = request.db_session.query(func.count(
            LoginMetric.user_id.distinct()
        )).filter(
            LoginMetric.created_at >= start_of_day
        ).scalar()

        # Возвращаем количество загруженных файлов
        count_files = request.db_session.query(func.count(
            Document.id
        )).scalar()

        # Возвращаем количество файлов загруженных сегодня
        count_files_today = request.db_session.query(func.count(
            Document.id
        )).filter(
            Document.created_at >= start_of_day
        ).scalar()
        return jsonify({
            "count_reg_users": count_reg_users,
            "count_return_users": count_return_users,
            "count_return_users_today": count_return_users_today,
            "count_files": count_files,
            "count_files_today": count_files_today,
        })


class VersionView(MethodView):
    """
    Класс для получения версии API
    """

    def get(self):
        return jsonify({"version": APP_VERSION})


class RegistrationView(BaseView):
    """
    Класс для регистрации пользователя
    """

    def post(self):
        validation_data = validate(UserSchema, **request.json)
        logger.info(f"Получены данные для регистрации: {validation_data}")
        if isinstance(validation_data, UserSchema):
            try:
                if get_user_by_email(email=validation_data.email) is False:
                    user = add_user(
                        email=validation_data.email,
                        password=validation_data.password
                    )

                    access_token = create_access_token(
                        identity=str(user.id),
                        expires_delta=timedelta(days=1)
                    )
                    refresh_token = create_refresh_token(
                        identity=str(user.id),
                        expires_delta=timedelta(days=7)
                    )

                    return jsonify({
                        "access_token": f"Bearer {access_token}",
                        "refresh_token": f"Bearer {refresh_token}"
                    }), 201

                else:
                    logger.error(f"Пользователь с таким email уже существует: {validation_data.email}")
                    raise HttpError(400, "User already exists")

            except SQLAlchemyError as e:
                self.handle_error(e, "User not created", 500)

        else:
            # Обрабатываем и выдаем сообщения об ошибке пользователю
            logger.error(f"Ошибка валидации данных регистрации: {validation_data}")
            self.handle_validation_errors(validation_data)


class LoginView(BaseView):
    """
    Класс для авторизации пользователя
    """

    def post(self):
        validation_data = validate(UserSchema, **request.json)
        logger.info(f"Получены данные для авторизации: {validation_data}")
        if isinstance(validation_data, UserSchema):
            try:
                user = get_user_by_email(email=validation_data.email)
                if user is False:
                    logger.error(f"Пользователь не найден: {validation_data.email}")
                    raise HttpError(404, "User not found")
            
                if check_password(
                    password=validation_data.password,
                    hashed_password=user.password
                ):
                    access_token = create_access_token(
                        identity=str(user.id),
                        expires_delta=timedelta(days=1)
                    )
                    refresh_token = create_refresh_token(
                        identity=str(user.id),
                        expires_delta=timedelta(days=7)
                    )

                    add_login_metric(user_id=user.id) # Добавление метрики входа

                    return jsonify({
                        "access_token": f"Bearer {access_token}",
                        "refresh_token": f"Bearer {refresh_token}"
                    }), 200

                else:
                    logger.error(f"Неверный пароль: {validation_data.password}")
                    raise HttpError(401, "Invalid password")

            except SQLAlchemyError as e:
                self.handle_error(e, "User not logged in", 500)

        else:
            # Обрабатываем и выдаем сообщения об ошибке пользователю
            logger.error(f"Ошибка валидации данных авторизации: {validation_data}")
            self.handle_validation_errors(validation_data)


class RefreshTokenView(BaseView):
    """
    Класс для обновления токена
    """

    @jwt_required(refresh=True)
    def post(self):
        try:
            access_token = create_access_token(
                identity=self.user_id,
                expires_delta=timedelta(days=1)
            )

            return jsonify({"access_token": f"Bearer {access_token}"}), 200

        except Exception as e:
            self.handle_error(e, "Token not updated", 500)


class UserView(BaseView):
    """
    Класс для получения, обновления и удаления данных пользователя
    """

    @jwt_required()
    def get(self):
        try:
            user = get_user_by_id(user_id=self.user_id)
            if user is False:
                logger.error(f"Пользователь не найден: {self.user_id}")
                raise HttpError(404, "User not found")

        except SQLAlchemyError as e:
            self.handle_error(e, "Error retrieving user data", 500)

        validation_data = validate(UserGetSchemaResponse, **user.__dict__)
        if isinstance(validation_data, UserGetSchemaResponse):
            return jsonify({
                "user": validation_data.model_dump(exclude_none=True)
            }), 200

        else:
            logger.error(
                f"Ошибка валидации данных {validation_data}"
                f"от пользователя: {self.user_id}"
            )
            self.handle_validation_errors(validation_data)
    
    @jwt_required()
    def patch(self):
        logger.info(f"Пользователь {self.user_id} отправил данные {request.json}")
        validation_data = validate(UpdateUserSchema, **request.json)

        if isinstance(validation_data, UpdateUserSchema):
            try:
                if update_user(
                    user_id=self.user_id,
                    email=validation_data.email,
                    password=validation_data.password
                ) is False:
                    logger.error(f"Пользователь {self.user_id} не найден")
                    raise HttpError(404, "User not found")

                return jsonify({"message": "User updated successfully"}), 200

            except SQLAlchemyError as e:
                self.handle_error(e, "User not updated", 500)

        else:
            # Обрабатываем и выдаем сообщения об ошибке пользователю
            logger.error(f"Ошибка валидации данных {validation_data}")
            self.handle_validation_errors(validation_data)
    
    @jwt_required()
    def delete(self):
        try:
            user = get_user_by_id(user_id=self.user_id)
            if user is False:
                logger.error(f"Пользователь {self.user_id} не найден")
                raise HttpError(404, "User not found")
            
            request.db_session.delete(user)
            request.db_session.commit()

            return jsonify({"message": "User deleted successfully"}), 204

        except SQLAlchemyError as e:
            self.handle_error(e, "User not deleted", 500)


class UploadDocumentView(BaseView):
    """
    Класс для загрузки документа
    """

    @jwt_required()
    def post(self):
        try:
            file = request.files.get("file")
            if file is None:
                logger.error(f"Пользователь {self.user_id} не загрузил файл")
                raise HttpError(400, "File not uploaded")
            
            if check_extension_file(file.filename):

                try:
                    text = reading_file(file=file)
                    file = add_document(
                        name_file=file.filename,
                        text=text,
                        user_id=self.user_id
                    )
                    return jsonify({
                        "id": file.id,
                        "message": "Document uploaded successfully"
                    }), 201

                except IntegrityError as e:
                    self.handle_error(e, "Document already exists", 409)

                except SQLAlchemyError as e:
                    self.handle_error(e, "Document not uploaded", 500)
            else:
                logger.error(
                    f"Пользователь {self.user_id}"
                    f"загрузил файл с неподдерживаемым расширением"
                )
                raise HttpError(400, "Invalid file extension")

        except SQLAlchemyError as e:
            self.handle_error(e, "Document not uploaded", 500)


class DocumentListView(BaseView):
    """
    Класс для получения списка документов
    """

    @jwt_required()
    def get(self):
        try:
            documents = (request.db_session.query(Document)
            .options(joinedload(Document.user))
            .filter(Document.user_id == self.user_id)).all()

            if documents is False:
                raise HttpError(404, "Documents not found")

            documents_list = []
            for document in documents:
                validation_data = DocumentSchemaResponse(
                    id=document.id,
                    name_file=document.name_file
                )
                documents_list.append(validation_data.model_dump())

            return jsonify(documents_list), 200

        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения списка документов: {e}")
            self.handle_error(e, "Error processing getting list of documents", 500)


class DocumentGetPatchDeleteView(BaseView):
    """
    Класс для получения, обновления и удаления документа
    """

    @jwt_required()
    def get(self, document_id: int):
        try:
            document = get_document_user_by_id(
                user_id=self.user_id,
                document_id=document_id
            )
            if document is None:
                raise HttpError(404, "Document not found")
            
            validation_data = DocumentSchemaResponse(
                id=document.id,
                name_file=document.name_file
            )

            return jsonify(validation_data.model_dump()), 200

        except SQLAlchemyError as e:
            self.handle_error(e, "Error processing getting document", 500)
    
    @jwt_required()
    def patch(self, document_id: int):
        try:
            logger.info(f"Пользователь {self.user_id} отправил данные {request.json}")
            validation_data = validate(
                UpdateDocumentSchemaRequest,
                **request.json
            )

            if isinstance(validation_data, UpdateDocumentSchemaRequest):
                document = update_document(
                    user_id=self.user_id,
                    document_id=document_id,
                    **validation_data.model_dump(exclude_none=True)
                )
                if document is None:
                    logger.error(
                        f"Документ {document_id}"
                        f"пользователя {self.user_id} не найден"
                    )
                    raise HttpError(404, "Document not found")

                return jsonify({
                    "message": "Document updated successfully"
                }), 200

            else:
                # Обрабатываем и выдаем сообщения об ошибке пользователю
                self.handle_validation_errors(validation_data)

        except SQLAlchemyError as e:
            self.handle_error(e, "Document not updated", 500)

    @jwt_required()
    def delete(self, document_id: int):
        try:
            if delete_document(
                user_id=self.user_id,
                document_id=document_id
            ) is None:
                raise HttpError(404, "Document not found")

            return jsonify({
                "message": "Document deleted successfully"
            }), 204

        except SQLAlchemyError as e:
            self.handle_error(e, "Document not deleted", 500)


class DocumentCollectionStatisticsView(BaseView):
    """
    Класс для получения статистики документа в коллекции
    """

    @jwt_required()
    def get(self, document_id: int):
        try:
            document = get_document_user_by_id(
                user_id=self.user_id,
                document_id=document_id
            )
            if document is None:
                raise HttpError(404, "Document not found")

            # Получаем id коллекций, к которым принадлежит документ
            collection_ids = (
                request.db_session.query(DocumentCollectionAssociation.c.collection_id)
                .filter(DocumentCollectionAssociation.c.document_id == document.id)
                .all()
            )
            if collection_ids is False:
                raise HttpError(404, "The document is not in the collection")
            
            collection_ids = [coll_id[0] for coll_id in collection_ids]

            # Получаем документы из коллекции, кроме текущего
            documents_statistic = []
            for collection_id in collection_ids:
                documents_in_collections = (
                    request.db_session.query(Document.data)
                    .join(DocumentCollectionAssociation, Document.id == DocumentCollectionAssociation.c.document_id)
                    .filter(DocumentCollectionAssociation.c.collection_id == collection_id)
                    .where(Document.id != document_id)
                    .all()
                )
                documents_list = [doc[0] for doc in documents_in_collections]

                tf_idf_data = calculate_tf_idf_for_document(
                    document=document.data,
                    collection=documents_list
                )

                documents_statistic.append(
                    {
                        "collection_id": collection_id,
                        "tf_idf_data": tf_idf_data.to_dict(orient="records")
                    }
                )

            return jsonify(documents_statistic), 200

        except SQLAlchemyError as e:
            self.handle_error(e, "Error processing getting list of documents", 500)


class CollectionDocumentListView(BaseView):
    """
    Класс для получения и создания коллекции
    """

    @jwt_required()
    def get(self):
        try:
            collections = (request.db_session.query(Collection)
            .options(joinedload(Collection.documents))
            .filter(Collection.user_id == self.user_id)).all()

            if not collections:
                raise HttpError(404, "Collections not found")
            
            # Проходим по коллекциям, валидируем данные и добавляем в список
            collections_list = []
            for collection in collections:
                validation_data = CollectionListSchemaResponse(
                    id=collection.id,
                    files=[
                        DocumentSchemaResponse(
                            id=doc.id,
                            name_file=doc.name_file
                        )
                        for doc in collection.documents
                    ]
                )

                # Предваительно сериализуем данные методом model_dump()
                collections_list.append(validation_data.model_dump())

            return jsonify(collections_list), 200

        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения списка коллекций: {e}")
            self.handle_error(e, "Error processing getting list of collections", 500)

    @jwt_required()
    def post(self):

        logger.info(f"Пользователь {self.user_id} отправил данные {request.json}")
        validation_data = validate(CollectionCreateSchemaRequest, **request.json)

        if isinstance(validation_data, CollectionCreateSchemaRequest):
            try:
                collection = add_collection(
                    user_id=self.user_id,
                    name=validation_data.name_collection
                )
                if collection:
                    return jsonify({
                        "id": collection.id,
                        "message": "Collection created successfully"
                    }), 201

            except IntegrityError as e:
                self.handle_error(e, "Collection already exists", 400)
            except SQLAlchemyError as e:
                self.handle_error(e, "Error processing creating collection", 500)

        else:
            logger.error(f"Ошибка валидации данных {validation_data}")
            self.handle_validation_errors(validation_data)


class CollectionView(BaseView):
    """
    Класс для получения и удаления коллекции
    """

    @jwt_required()
    def get(self, collection_id: int):
        try:
            document_ids = (
                request.db_session.query(DocumentCollectionAssociation.c.document_id)
                .filter(DocumentCollectionAssociation.c.collection_id == collection_id)
            ).all()

            if document_ids is None:
                raise HttpError(404, "No documents found in the collection")

            validation_data = CollectionGetSchemaResponse(
                documents_id=[doc_id[0] for doc_id in document_ids]
            )

            return jsonify(validation_data.model_dump()), 200

        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения коллекции: {e}")
            self.handle_error(e, "Error processing getting collection", 500)

    @jwt_required()
    def delete(self, collection_id: int):
        try:
            collection = delete_collection(
                user_id=self.user_id,
                collection_id=collection_id
            )
            if collection is None:
                raise HttpError(404, "Collection not found")

            return jsonify({"message": "Collection deleted successfully"}), 204

        except SQLAlchemyError as e:
            self.handle_error(e, "Collection not deleted", 500)


class CollectionStatisticsView(BaseView):
    """
    Класс для получения статистики коллекции
    """

    @jwt_required()
    def get(self, collection_id: int):
        try:
            # Получаем документы из коллекции
            documents = (
                request.db_session.query(Document)
                .options(joinedload(Document.collections))
                .filter(Document.collections.any(Collection.id == collection_id))
            ).all()
            
            if documents is False:
                raise HttpError(
                    404,
                    "No documents found in the collection"
                )

            documents_list = []
            for document in documents:
                documents_list.append(document.data)

            # Вычисляем TF-IDF предварительно объединив тексты документов
            tf_idf_data = process_text(text=' '.join(documents_list))

            return jsonify(tf_idf_data.to_dict(orient="records")), 200

        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения коллекции: {e}")
            self.handle_error(e, "Error processing getting collection", 500)


class DocumentCollectionCreateDeleteView(BaseView):
    """
    Класс для добавления и удаления документа в(из) коллекцию(ии)
    """

    @jwt_required()
    def post(self, collection_id: int, document_id: int):
        try:
            document = get_document_user_by_id(
                user_id=self.user_id,
                document_id=document_id
            )
            if document is None:
                raise HttpError(404, "Document not found")

            collection = get_collection_user_by_id(
                user_id=self.user_id,
                collection_id=collection_id
            )
            if collection is None:
                raise HttpError(404, "Collection not found")

            add_document_to_collection(
                collection_id=collection_id,
                document_id=document_id
            )

            return jsonify({
                "message": "Document added to collection successfully"
            }), 200

        except SQLAlchemyError as e:
            self.handle_error(
                error=e,
                message="Error processing adding document to collection",
                status_code=500
            )
    
    @jwt_required()
    def delete(self, collection_id: int, document_id: int):
        try:
            document = get_document_user_by_id(
                user_id=self.user_id,
                document_id=document_id
            )
            if document is None:
                raise HttpError(404, "Document not found")

            collection = get_collection_user_by_id(
                user_id=self.user_id,
                collection_id=collection_id
            )
            if collection is None:
                raise HttpError(404, "Collection not found")

            delete_document_from_collection(
                collection_id=collection_id,
                document_id=document_id
            )

            return jsonify({
                "message": "Document deleted from collection successfully"
            }), 204

        except SQLAlchemyError as e:
            self.handle_error(
                error=e,
                message="Error processing deleting document from collection",
                status_code=500
            )


app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/status/",
    view_func=StatusView.as_view("status")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/metrics/",
    view_func=MetricsView.as_view("metrics")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/version/",
    view_func=VersionView.as_view("version")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/register/",
    view_func=RegistrationView.as_view("register")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/login/",
    view_func=LoginView.as_view("login")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/refresh_token/",
    view_func=RefreshTokenView.as_view("refresh_token")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/user/",
    view_func=UserView.as_view("user")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/upload_document/",
    view_func=UploadDocumentView.as_view("upload_document")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/documents/",
    view_func=DocumentListView.as_view("documents")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/documents/<int:document_id>",
    view_func=DocumentGetPatchDeleteView.as_view("document")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/documents/<int:document_id>/statistics",
    view_func=DocumentCollectionStatisticsView.as_view("document_statistics")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/collections/",
    view_func=CollectionDocumentListView.as_view("collections")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/collections/<int:collection_id>",
    view_func=CollectionView.as_view("collection")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/collections/<int:collection_id>/statistics",
    view_func=CollectionStatisticsView.as_view("collection_statistics")
)
app.add_url_rule(
    f"{API_VERSION_URL_PREFIX_V1}/collections/<int:collection_id>/<int:document_id>",
    view_func=DocumentCollectionCreateDeleteView.as_view("collection_document_add_delete")
)

if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_API_HOST", "localhost"), port=os.getenv("FLASK_API_PORT", 5050))