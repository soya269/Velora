import os
import uuid
from functools import wraps
from urllib.parse import urlsplit

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from models.user import User
from extensions import db, limiter
from . import admin_bp


# ==========================================
# ALLOWED PROFILE IMAGE TYPES
# ==========================================

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp"
}


# ==========================================
# GET PROFILE IMAGE
# ==========================================

def get_user_profile_image(user):
    """
    Get the profile image path from the User model.

    Supports both:
        user.image
        user.profile
    """

    image = None

    if hasattr(user, "image"):
        image = getattr(user, "image", None)

    if not image and hasattr(user, "profile"):
        image = getattr(user, "profile", None)

    if not image:
        return None

    # Convert Windows path to web path
    image = str(image).replace("\\", "/")

    # Remove possible prefixes
    if image.startswith("static/"):
        image = image[7:]

    if image.startswith("/static/"):
        image = image[8:]

    if image.startswith("/"):
        image = image.lstrip("/")

    return image


# ==========================================
# ADMIN REQUIRED
# ==========================================

def admin_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        # User is not logged in
        if "user" not in session:

            return redirect(
                url_for(
                    "admin.admin_login",
                    next=request.path
                )
            )

        # User must be Admin or Staff
        if session["user"].get("role") not in (
            "Admin",
            "Staff"
        ):

            flash(
                "Administrator access required.",
                "danger"
            )

            return redirect(
                url_for("front.home")
            )

        return fn(*args, **kwargs)

    return wrapper


# ==========================================
# ADMIN LOGIN
# ==========================================

@admin_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def admin_login():

    if request.method == "POST":

        identity = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # Find user by username OR email
        user = User.query.filter(
            (User.username == identity) |
            (User.email == identity.lower())
        ).first()

        # Validate login
        if (
            not user
            or not check_password_hash(
                user.password,
                password
            )
            or user.status != "Active"
            or user.role != "Admin"
        ):

            flash(
                "Invalid administrator credentials.",
                "danger"
            )

            return redirect(
                url_for("admin.admin_login")
            )

        # ==========================================
        # GET PROFILE IMAGE
        # ==========================================

        profile_image = get_user_profile_image(user)

        # ==========================================
        # SAVE USER TO SESSION
        # ==========================================

        session["user"] = {

            "id": user.id,

            "name": user.name,

            "username": user.username,

            "email": user.email,

            "role": user.role,

            "image": profile_image,

            "profile": profile_image
        }

        session.modified = True

        # ==========================================
        # REDIRECT
        # ==========================================

        next_page = request.args.get("next", "")

        # Only allow same-host relative paths to prevent open redirects.
        target = urlsplit(next_page)
        if next_page and not target.netloc and not target.scheme and next_page.startswith("/") and not next_page.startswith("//"):
            return redirect(next_page)

        return redirect(
            url_for("admin.admin_dashboard")
        )

    return render_template(
        "front/admin/login.html"
    )


# ==========================================
# ADMIN PROFILE
# ==========================================

@admin_bp.route("/profile", methods=["GET", "POST"])
@admin_required
def admin_profile():

    # Get logged-in admin ID
    user_id = session["user"].get("id")

    # Get actual user from database
    user = User.query.get(user_id)

    if not user:

        session.pop("user", None)

        flash(
            "Administrator account not found.",
            "danger"
        )

        return redirect(
            url_for("admin.admin_login")
        )

    # ==========================================
    # UPDATE PROFILE
    # ==========================================

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        username = request.form.get(
            "username",
            ""
        ).strip()

        # ==========================================
        # VALIDATE NAME
        # ==========================================

        if not name:

            flash(
                "Name is required.",
                "danger"
            )

            return redirect(
                url_for("admin.admin_profile")
            )

        # ==========================================
        # VALIDATE USERNAME
        # ==========================================

        if not username:

            flash(
                "Username is required.",
                "danger"
            )

            return redirect(
                url_for("admin.admin_profile")
            )

        # ==========================================
        # CHECK DUPLICATE USERNAME
        # ==========================================

        existing_user = User.query.filter(
            User.username == username,
            User.id != user.id
        ).first()

        if existing_user:

            flash(
                "Username is already taken.",
                "danger"
            )

            return redirect(
                url_for("admin.admin_profile")
            )

        # ==========================================
        # UPDATE NAME
        # ==========================================

        user.name = name

        # ==========================================
        # UPDATE USERNAME
        # ==========================================

        user.username = username

        # ==========================================
        # PROFILE IMAGE
        # ==========================================

        image = request.files.get(
            "profile_image"
        )

        if image and image.filename:

            filename = secure_filename(
                image.filename
            )

            if not filename:

                flash(
                    "Invalid image file.",
                    "danger"
                )

                return redirect(
                    url_for("admin.admin_profile")
                )

            # Get extension
            extension = os.path.splitext(
                filename
            )[1].lower().replace(".", "")

            # Validate extension
            if extension not in ALLOWED_IMAGE_EXTENSIONS:

                flash(
                    "Only JPG, JPEG, PNG, GIF and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for("admin.admin_profile")
                )

            # ==========================================
            # UPLOAD DIRECTORY
            # ==========================================

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "users"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            # ==========================================
            # UNIQUE FILE NAME
            # ==========================================

            new_filename = (
                f"{uuid.uuid4().hex}."
                f"{extension}"
            )

            file_path = os.path.join(
                upload_folder,
                new_filename
            )

            # ==========================================
            # SAVE IMAGE
            # ==========================================

            image.save(file_path)

            # ==========================================
            # DATABASE PATH
            # ==========================================

            image_path = (
                f"uploads/users/{new_filename}"
            )

            # Save to image column
            if hasattr(user, "image"):

                user.image = image_path

            # Save to profile column
            if hasattr(user, "profile"):

                user.profile = image_path

        # ==========================================
        # SAVE DATABASE
        # ==========================================

        try:

            db.session.commit()

        except Exception as error:

            db.session.rollback()

            print(
                "ADMIN PROFILE UPDATE ERROR:",
                error
            )

            flash(
                "Unable to update administrator profile.",
                "danger"
            )

            return redirect(
                url_for("admin.admin_profile")
            )

        # ==========================================
        # GET UPDATED IMAGE
        # ==========================================

        profile_image = get_user_profile_image(
            user
        )

        # ==========================================
        # UPDATE SESSION
        # ==========================================

        session["user"] = {

            "id": user.id,

            "name": user.name,

            "username": user.username,

            "email": user.email,

            "role": user.role,

            "image": profile_image,

            "profile": profile_image
        }

        session.modified = True

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.admin_profile")
        )

    # ==========================================
    # GET CURRENT IMAGE
    # ==========================================

    profile_image = get_user_profile_image(
        user
    )

    # ==========================================
    # PROFILE DATA FOR TEMPLATE
    # ==========================================

    current_user = {

        "id": user.id,

        "name": user.name,

        "username": user.username,

        "email": user.email,

        "role": user.role,

        "image": profile_image,

        "profile": profile_image
    }

    # ==========================================
    # RENDER PROFILE
    # ==========================================

    return render_template(
        "front/admin/profile.html",
        current_user=current_user
    )