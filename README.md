# Веб-приложение для получения данных tf-idf из текстовых файлов (txt, docx, pdf)
Версия 1.0.1

## Описание

Веб-приложение загружает текстовый файл (txt, docx, pdf) до 10МБ, обрабатывает его, выдает таблицу в формате:

|    Слово    |      TF     |      IDF      |
| :---        |    :----:   |     ---:      |
| павловна    | 0           | 0.280649363   |
| анна	      | 0	        | 0.280649363   |

## Поддерживает

- Регистрация, авторизация, аутентификация
- Хэширование паролей
- Миграции
- Валидацию по email и паролю
- Пагинацию
- Проверку расширений файлов

## Начало работы

- В файле ```.env``` задать переменные для создания БД и сгенерировать [секретный ключ](https://docs-python.ru/standart-library/modul-secrets-python/)
- В командной строке запустить ```docker-compose up -d``` (Для работы необходимо установить [Docker Desktop](https://www.docker.com/products/docker-desktop/))
  
## Стэк

- Flask v3.1.1
- Flask-Login v0.6.3
- SQLAlchemy v2.0.41
- PostgreSQL v15.4
- Docker-compose v2.34.0
- Bcrypt v4.3.0
- Pydantic v2.11.5
- Alembic v1.16.1
- Python-dotenv v1.1.0
- Python-docx v1.1.2
- PyPDF2 v3.0.1
- NLTK v3.9.1
- Pandas v2.2.3
- Scikit-learn v1.6.1