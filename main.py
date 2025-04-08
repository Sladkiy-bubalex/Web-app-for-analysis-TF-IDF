from config import SECRET_KEY, logger, ALLOWED_EXTENSIONS
from dependencies import Session
from schemas import UserSchema, validate
from authentication import check_password
from models import User
from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
    LoginManager,
)
from flask import (
    Flask,
    request,
    render_template,
    flash, redirect,
    Response,
    url_for
)
from functions.functions_main import (
    check_extension_file,
    process_text,
    pagination,
    get_user,
    add_data_tf_idf,
    get_file,
    add_user,
    reading_file,
)


app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return request.db_session.get(User, user_id)


@app.before_request
def before_request():
    request.db_session = Session()


@app.after_request
def after_request(reponse: Response):
    request.db_session.close()
    return reponse


@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("login"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("download_file"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        check_data = validate(
            schema_cls=UserSchema,
            email=email,
            password=password
        )
        if isinstance(check_data, UserSchema):
            try:
                user = get_user(email=email)
                if user and check_password(password, user.password):
                    rm = True if request.form.get("remember-me") else False
                    login_user(user, remember=rm)
                    return redirect(url_for("download_file"))
                else:
                    flash("Email или пароль не верные.")
                    return redirect(request.url)
            except Exception as e:
                logger.error(f"Ошибка входа {e}")
                flash("Произошла ошибка входа, попробуйте позже.")
                return redirect(request.url)

    return render_template("login.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        check_data = validate(
            schema_cls=UserSchema,
            email=email,
            password=password
        )
        if isinstance(check_data, UserSchema):
            try:
                if get_user(email=email) is False:
                    user = add_user(email=email, password=password)
                    rm = True if request.form.get("remember-me") else False
                    login_user(user, remember=rm)
                    return redirect(url_for("download_file"))
                else:
                    flash("Пользователь с таким email уже существует.")
                    return redirect(request.url)
            except Exception as e:
                logger.error(f'Ошибка регистрации пользователя {email}: {e}')
                flash("Произошла ошибка регистрации, попробуйте позже.")
                return redirect(request.url)

        elif (
            check_data[0]["type"] == "value_error"
        ):  # Дополнительное информирования о длинне пароля.
            flash(check_data[0]["msg"].split(",")[1])
            return redirect(request.url)

        else:
            flash("Не верно введенные данные.")
            return redirect(request.url)

    return render_template("registration.html")


@app.route("/download_file/", methods=["GET", "POST"])
@login_required
def download_file():

    if request.method == "POST":
        if "file" not in request.files:
            flash("Не удалось прочитать файл.")
            return redirect(request.url)

        uploaded_file = request.files.get('file')

        if uploaded_file.filename == "":
            flash("Файл отсутсвует")
            return redirect(request.url)

        if uploaded_file and check_extension_file(uploaded_file.filename):
            text = reading_file(file=uploaded_file)
            try:
                add_file = add_data_tf_idf(
                    name_file=uploaded_file.filename, text=text, user_id=current_user.id
                )
                return redirect(f"/tf_idf/?file_id={add_file.id}")
            except Exception as e:
                logger.error(
                    f"Ошибка при обработке файла: {uploaded_file.filename} : {e}."
                )
                flash("Произошла ошибка обработки файла, повторите попытку.")
                return redirect(request.url)

        else:
            flash("Не корректное расширение файла.")
            return redirect(request.url)

    return render_template("download.html", extensions=ALLOWED_EXTENSIONS)


@app.route("/tf_idf/", methods=["GET"])
@login_required
def tf_idf():
    file_id = request.args.get("file_id")
    if file_id is None:
        flash("Файл не загружен.")
        return redirect(url_for("download_file"))

    try:
        file = get_file(file_id=file_id)
        if file:
            df_file = process_text(file.data)
            page = request.args.get("page", 1, type=int)
            items, total_pages = pagination(data_frame=df_file, page=page)
            return render_template(
                "result.html", items=items, total_pages=total_pages, page=page
            )
        else:
            logger.error("Файл ")
            flash("У вас нет такого файла, попробуйте загрузить снова.")
            return redirect(url_for("donwload_file"))

    except Exception as e:
        logger.error(
            f"Ошибка вывода информации из файла по id: {file_id} - {e}"
        )
        flash("Ошибка вывода информации, попробуйте позже.")
        return redirect(url_for("download_file"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("root"))


if __name__ == "__main__":
    app.run(debug=True)
