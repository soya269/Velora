from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import front_bp
from models.user import User
from extensions import db, limiter

def login_user(user):
    session.clear()
    session["user"] = {"id": user.id, "name": user.name, "username": user.username,
                       "email": user.email, "role": user.role, "profile": user.profile}
    session.permanent = True

@front_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if request.method == "POST":
        identity = request.form.get("username", request.form.get("email", "")).strip()
        password = request.form.get("password", "")
        user = User.query.filter((User.username == identity) | (User.email == identity)).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid username/email or password.", "danger")
            return redirect(url_for("front.login"))
        if user.status != "Active":
            flash("This account is inactive. Please contact the administrator.", "warning")
            return redirect(url_for("front.login"))
        login_user(user)
        flash("Login successful.", "success")
        return redirect(url_for("front.account"))
    return render_template("front/front/login.html")

@front_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def register():
    if request.method == "POST":
        first=request.form.get("first_name","").strip()
        last=request.form.get("last_name","").strip()
        name=request.form.get("name","").strip() or " ".join(x for x in [first,last] if x)
        email=request.form.get("email","").strip().lower()
        username=request.form.get("username","").strip() or email.split("@")[0]
        password=request.form.get("password","")
        confirm=request.form.get("confirm_password","")
        if not all([name, username, email, password]):
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("front.register"))
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("front.register"))
        if User.query.filter((User.username==username)|(User.email==email)).first():
            flash("Username or email already exists.", "danger")
            return redirect(url_for("front.register"))
        user=User(name=name, username=username, email=email,
                  password=generate_password_hash(password), role="Staff", status="Active")
        db.session.add(user); db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("front.login"))
    return render_template("front/front/register.html")

# @front_bp.route("/logout")
# def logout():
#     session.clear()
#     flash("You have been logged out.", "success")
#     return redirect(url_for("front.home"))
@front_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("front.login"))
@front_bp.route("/account")
def account():
    if "user" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("front.login"))
    user=User.query.get(session["user"]["id"])
    if not user:
        session.clear(); return redirect(url_for("front.login"))
    return render_template("front/front/account.html", user=user, orders=user.orders)

@front_bp.route("/forgot-password", methods=["GET","POST"])
def forgot_password():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower()
        if User.query.filter_by(email=email).first():
            return render_template("front/front/reset_password.html", email=email)
        flash("Email not found.", "danger")
    return render_template("front/front/forgot-password.html")

@front_bp.route("/reset-password", methods=["POST"])
@limiter.limit("10 per minute")
def reset_password():
    email=request.form.get("email","").strip().lower()
    password=request.form.get("password","")
    confirm=request.form.get("confirm_password","")
    if password != confirm or not password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("front.forgot_password"))
    user=User.query.filter_by(email=email).first()
    if not user:
        flash("Email not found.", "danger")
        return redirect(url_for("front.forgot_password"))
    user.password=generate_password_hash(password)
    db.session.commit()
    flash("Password reset successfully. Please login.", "success")
    return redirect(url_for("front.login"))
