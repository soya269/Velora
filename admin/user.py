import os
import uuid

from flask import render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from extensions import db, limiter
from models.user import User
from . import admin_bp
from .auth import admin_required

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def save_profile(file):
    if not file or not file.filename:
        return None
    filename = secure_filename(file.filename)
    if "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    new_filename = f"user_{uuid.uuid4().hex}.{ext}"
    folder = current_app.config["USER_UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, new_filename))
    return new_filename

def remove_profile(filename):
    if not filename:
        return
    path = os.path.join(current_app.config["USER_UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        os.remove(path)

@admin_bp.route("/users")
@admin_required
def admin_users():
    users = User.query.order_by(User.id.desc()).all()
    return render_template("front/admin/users/index.html", users=users, rows=users)

@admin_bp.route("/users/create", methods=["GET", "POST"])
@admin_required
@limiter.limit("60 per minute")
def create_user():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "Staff")
        status = request.form.get("status", "Active")

        if not all([name, username, email, password]):
            flash("Please fill in all required fields.", "danger")
            return render_template("front/admin/users/create.html")
        if role not in {"Admin", "Staff"}: role = "Staff"
        if status not in {"Active", "Inactive"}: status = "Active"

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists.", "danger")
            return render_template("front/admin/users/create.html")

        profile = save_profile(request.files.get("profile"))
        user = User(name=name, username=username, email=email,
                    password=generate_password_hash(password), role=role, status=status, profile=profile)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            if profile: remove_profile(profile)
            flash("Could not save the user to the database.", "danger")
            return render_template("front/admin/users/create.html")

        flash("User created successfully.", "success")
        return redirect(url_for("admin.admin_users"))
    return render_template("front/admin/users/create.html")

@admin_bp.route("/users/edit/<int:id>", methods=["GET", "POST"])
@admin_required
@limiter.limit("60 per minute")
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "Staff")
        status = request.form.get("status", "Active")
        if not all([name, username, email]):
            flash("Name, username and email are required.", "danger")
            return redirect(url_for("admin.edit_user", id=id))
        duplicate = User.query.filter(User.id != id, ((User.username == username) | (User.email == email))).first()
        if duplicate:
            flash("Username or email already exists.", "danger")
            return redirect(url_for("admin.edit_user", id=id))
        user.name, user.username, user.email = name, username, email
        user.role = role if role in {"Admin", "Staff"} else "Staff"
        user.status = status if status in {"Active", "Inactive"} else "Active"
        password = request.form.get("password", "").strip()
        if password:
            user.password = generate_password_hash(password)
        old_profile = user.profile
        new_profile = save_profile(request.files.get("profile"))
        if new_profile:
            user.profile = new_profile
        try:
            db.session.commit()
            if new_profile and old_profile:
                remove_profile(old_profile)
        except Exception:
            db.session.rollback()
            if new_profile: remove_profile(new_profile)
            flash("Could not update the user.", "danger")
            return redirect(url_for("admin.edit_user", id=id))
        flash("User updated successfully.", "success")
        return redirect(url_for("admin.admin_users"))
    return render_template("front/admin/users/edit.html", user=user)

@admin_bp.route("/users/delete/<int:id>", methods=["POST"])
@admin_required
@limiter.limit("30 per minute")
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == session.get("user", {}).get("id"):
        flash("You cannot delete the account currently in use.", "danger")
        return redirect(url_for("admin.admin_users"))
    profile = user.profile
    try:
        db.session.delete(user)
        db.session.commit()
        remove_profile(profile)
        flash("User deleted successfully.", "success")
    except Exception:
        db.session.rollback()
        flash("Could not delete the user.", "danger")
    return redirect(url_for("admin.admin_users"))
