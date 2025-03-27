import datetime
import jwt
import os
from flask import request
from functools import wraps


def create_access_token(identifier="device"):
    payload = {
        "sub": identifier,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8),
        "iat": datetime.datetime.now(datetime.UTC),
    }
    return jwt.encode(payload, os.getenv("FLASK_SECRET_KEY"), algorithm="HS256")


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {"message": "Bearer token malformattato!"}, 401

            if not token:
                return {"message": "Token mancante!"}, 401

            try:
                payload = jwt.decode(
                    token, os.getenv("FLASK_SECRET_KEY"), algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                return {"message": "Token scaduto!"}, 401
            except jwt.InvalidTokenError:
                return {"message": "Token non valido!"}, 401

            return f(*args, **kwargs)
        else:
            return {"message": "Token mancante!"}, 401

    return decorated
