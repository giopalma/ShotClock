from functools import wraps
from flask import Response, request

from config import get_config


def check_auth(username, password):
    """
    Controlla se l'utente e la password sono corretti.
    TODO: Si potrebbe utilizzare il database e utilizzare metodi più sicuri e adatti.
    """
    config = get_config()
    return (
        username == config["WEB"]["Username"] and password == config["WEB"]["Password"]
    )


def http_basic_auth():
    """
    HTTP Basic Authentication per richiedere username e password
    """
    return Response(
        "Could not verify your access level for that URL.\n"
        "You have to login with proper credentials",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )


def requires_auth(f):
    """
    Decorator per richiedere l'autenticazione HTTP Basic per una determinata route
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return http_basic_auth()
        return f(*args, **kwargs)

    return decorated
