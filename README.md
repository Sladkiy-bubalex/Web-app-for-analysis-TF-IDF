# Веб-приложение для получения данных tf-idf из текстовых файлов (txt, docx, pdf)
Версия 1.3.4

## Описание

Веб-приложение загружает текстовый файл (txt, docx, pdf) до 5МБ, обрабатывает его, выдает отсортированную по IDF (по убыванию) таблицу (топ 50) в формате:

|    Слово    |      TF     |      IDF      |
| :---        |    :----:   |     ---:      |
| павловна    | 0           | 0.280649363   |
| анна	      | 0	        | 0.280649363   |

## Приложение поддерживает 

- Регистрацию, авторизацию, аутентификацию
  - Веб-приложение - сессии
  - API - JWT
- Миграции с помощью Alembic
- Валидацию
- Пагинацию
- Проверку расширений файлов

## Начало работы

### Установка на виртуальной машине (Linux)

- Установить [Git](https://git-scm.com/book/ru/v2/%D0%92%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D0%A3%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-Git)
- Установить [Docker](https://docs.docker.com/engine/install/ubuntu/)
- Установить [Docker Compose](https://docs.docker.com/desktop/setup/install/linux/)
- Клонировать репозитерий ```git clone https://github.com/Sladkiy-bubalex/Web-app-for-analysis-TF-IDF.git```
- Перейти в директорию ```cd ./Web-app-for-analysis-TF-IDF/```
- Создать файл ```.env```:
  - В файле ```.env``` задать переменные для создания БД:
    - ```POSTGRES_DB```
    - ```POSTGRES_USER```
    - ```POSTGRES_PASSWORD```
  - Cгенерировать [секретный ключ](https://docs-python.ru/standart-library/modul-secrets-python/) и внести его в переменную ```SECRET_KEY```
  - Аналогичным образом выше, сгененрировать ключ и внести его в переменную ```JWT_SECRET_KEY```
  - Задать переменные:
    - ```FLASK_APP_PORT=5000```
    - ```FLASK_APP_HOST=0.0.0.0```
    - ```FLASK_API_PORT=5050```
    - ```FLASK_API_HOST=0.0.0.0```
- В командной строке запустить ```docker-compose up -d```

## Структура проекта

Docker-compose создает 4 контейнера:

1. ```web``` - веб-приложение
2. ```api``` - API
3. ```postgres``` - база данных
4. ```nginx``` - Nginx

- Все запросы принимаются на ```http://your_ip_address:80```
- Документация к API генерируется по URL ```http://your_ip_address:80/apidocs```
- Схема к БД [здесь](./Schema_db.drawio.png)

## Стэк

- Flask v3.1.1
- Flask-Login v0.6.3
- Flask-JWT-Extended v5.5.1
- Flasgger v0.9.5
- SQLAlchemy v2.0.41
- PostgreSQL v15.4
- Bcrypt v4.3.0
- Pydantic v2.11.5
- Alembic v1.16.1
- Python-dotenv v1.1.0
- Python-docx v1.1.2
- PyPDF2 v3.0.1
- NLTK v3.9.1
- Pandas v2.2.3
- Scikit-learn v1.6.1