from flask import Blueprint, jsonify
from config import APP_VERSION
from models import LoginMetric, User, Sorted_Tfidf
from flask import request
from sqlalchemy import func
from datetime import datetime, time


api = Blueprint("api", __name__)

@api.route("/status/", methods=["GET"])
def status():
    return jsonify({"status": "OK"})

@api.route("/metrics/", methods=["GET"])
def metrics():
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
        Sorted_Tfidf.id
    )).scalar()

    # Возвращаем количество файлов загруженных сегодня
    count_files_today = request.db_session.query(func.count(
        Sorted_Tfidf.id
    )).filter(
        Sorted_Tfidf.created_at >= start_of_day
    ).scalar()
    return jsonify({
        "count_reg_users": count_reg_users,
        "count_return_users": count_return_users,
        "count_return_users_today": count_return_users_today,
        "count_files": count_files,
        "count_files_today": count_files_today,
    })

@api.route("/version/", methods=["GET"])
def version():
    return jsonify({"version": APP_VERSION})