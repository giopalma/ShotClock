import datetime
import jwt
import os
from flask import request
from functools import wraps
import logging


def create_access_token(identifier="device"):
    payload = {
        "sub": identifier,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8),
        "iat": datetime.datetime.now(datetime.UTC),
    }
    return jwt.encode(payload, os.getenv("FLASK_SECRET_KEY"), algorithm="HS256")


def check_auth():
    token = request.cookies.get("access_token")
    if token:
        try:
            jwt.decode(token, os.getenv("FLASK_SECRET_KEY"), algorithms=["HS256"])
            return True
        except:
            return False
    else:
        raise Exception("No token found")


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            check_auth()
            return f(*args, **kwargs)
        except Exception as e:
            return {"message": "Token mancante!"}, 401

    return decorated
