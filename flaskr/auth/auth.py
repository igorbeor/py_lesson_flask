import functools
import json
from flask import jsonify
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from flask_httpauth import HTTPBasicAuth
from flask import Response

from flaskr.db import get_db
from flaskr.auth.queries import (
    create_user, get_user_by_id, get_user_by_username
)

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = get_user_by_username(get_db(), username)
    if user:
        return check_password_hash(user["password"], password)
    return False

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    db = get_db()
    error = None
        
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if not username:
        error = "Username is required."
    elif not password:
        error = "Password is required."
    elif get_user_by_username(db, username) is not None:
        error = "User {0} is already registered.".format(username)

    if error:
        error = json.dumps({"error": error})
        return Response(
            error,
            status=400,
            mimetype="application/json"
        )
    
    create_user(db, username, password)
    user = get_user_by_username(db, username)
    data = {"user_id": user["id"], "username": user["username"]}
    data = json.dumps(data)
    return Response(
        data,
        status=200,
        mimetype="application/json"
    )


@bp.route("/logout")
@auth.login_required
def logout():
    data = json.dumps({'response': 'Logout successfully'})
    return Response(
        data,
        status=401,
        mimetype="application/json"
    )
