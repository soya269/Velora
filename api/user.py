"""Administrator-only user management API."""
from functools import wraps

from flask import jsonify, request, session
from werkzeug.security import generate_password_hash

from extensions import db, limiter
from models import User
from . import api_bp


ALLOWED_ROLES = {"Admin", "Staff"}
ALLOWED_STATUSES = {"Active", "Inactive"}


def admin_api_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        current_user = session.get("user") or {}
        if current_user.get("role") != "Admin":
            return jsonify({
                "success": False,
                "message": "Administrator authentication required.",
            }), 401
        return view(*args, **kwargs)
    return wrapped


def user_data(user):
    return user.to_dict()


def _duplicate_user(username, email, exclude_id=None):
    query = User.query.filter(
        (User.username == username) | (User.email == email)
    )
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    return query.first()


@api_bp.route("/users", methods=["GET"])
@admin_api_required
def get_users():
    users = User.query.order_by(User.id.desc()).all()
    return jsonify({"success": True, "users": [user_data(u) for u in users]})


@api_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_api_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"success": True, "user": user_data(user)})


@api_bp.route("/users", methods=["POST"])
@limiter.limit("60 per minute")
@admin_api_required
def create_user():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    role = data.get("role", "Staff")
    status = data.get("status", "Active")

    if not all((name, username, email, password)):
        return jsonify({
            "success": False,
            "message": "name, username, email and password are required",
        }), 400
    if role not in ALLOWED_ROLES or status not in ALLOWED_STATUSES:
        return jsonify({"success": False, "message": "Invalid role or status."}), 400
    if _duplicate_user(username, email):
        return jsonify({"success": False, "message": "Username or email already exists."}), 409

    user = User(
        name=name,
        username=username,
        email=email,
        password=generate_password_hash(password),
        role=role,
        status=status,
    )
    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Could not create user."}), 500
    return jsonify({"success": True, "user": user_data(user)}), 201


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@limiter.limit("60 per minute")
@admin_api_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", user.name)).strip()
    username = str(data.get("username", user.username)).strip()
    email = str(data.get("email", user.email)).strip().lower()
    role = data.get("role", user.role)
    status = data.get("status", user.status)

    if not all((name, username, email)):
        return jsonify({"success": False, "message": "Name, username and email are required."}), 400
    if role not in ALLOWED_ROLES or status not in ALLOWED_STATUSES:
        return jsonify({"success": False, "message": "Invalid role or status."}), 400
    if _duplicate_user(username, email, exclude_id=user.id):
        return jsonify({"success": False, "message": "Username or email already exists."}), 409

    user.name = name
    user.username = username
    user.email = email
    user.role = role
    user.status = status
    if data.get("password"):
        user.password = generate_password_hash(str(data["password"]))

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Could not update user."}), 500
    return jsonify({"success": True, "user": user_data(user)})


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@limiter.limit("30 per minute")
@admin_api_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == (session.get("user") or {}).get("id"):
        return jsonify({"success": False, "message": "You cannot delete the account currently in use."}), 400
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Could not delete user."}), 500
    return jsonify({"success": True, "message": "User deleted successfully."})
