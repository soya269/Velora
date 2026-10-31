import os, uuid
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from extensions import db, limiter
from models.category import Category
from . import admin_bp
from .auth import admin_required

ALLOWED={"png","jpg","jpeg","gif","webp"}
def save_image(file):
    if not file or not file.filename: return None
    safe=secure_filename(file.filename)
    if "." not in safe or safe.rsplit(".",1)[1].lower() not in ALLOWED: return None
    ext=safe.rsplit(".",1)[1].lower(); name=f"category_{uuid.uuid4().hex}.{ext}"
    folder=current_app.config["CATEGORY_UPLOAD_FOLDER"]; os.makedirs(folder,exist_ok=True); file.save(os.path.join(folder,name)); return name
def remove_image(name):
    if name:
        path=os.path.join(current_app.config["CATEGORY_UPLOAD_FOLDER"],name)
        if os.path.isfile(path): os.remove(path)

@admin_bp.route("/categories")
@admin_required
def admin_categories():
    return render_template("front/admin/categories/index.html", categories=Category.query.order_by(Category.id.desc()).all())

@admin_bp.route("/categories/create", methods=["GET","POST"])
@admin_required
@limiter.limit("60 per minute")
def create_category():
    if request.method=="POST":
        name=request.form.get("name","").strip(); description=request.form.get("description","").strip()
        if not name: flash("Category name is required.","danger"); return render_template("front/admin/categories/create.html")
        if Category.query.filter_by(name=name).first(): flash("Category already exists.","danger"); return render_template("front/admin/categories/create.html")
        c=Category(name=name,description=description,image=save_image(request.files.get("image")))
        db.session.add(c); db.session.commit(); flash("Category created successfully.","success"); return redirect(url_for("admin.admin_categories"))
    return render_template("front/admin/categories/create.html")

@admin_bp.route("/categories/edit/<int:id>", methods=["GET","POST"])
@admin_required
def edit_category(id):
    c=Category.query.get_or_404(id)
    if request.method=="POST":
        name=request.form.get("name","").strip(); description=request.form.get("description","").strip()
        duplicate=Category.query.filter(Category.id!=id,Category.name==name).first()
        if not name or duplicate: flash("Valid unique category name is required.","danger"); return redirect(url_for("admin.edit_category",id=id))
        c.name=name; c.description=description; old=c.image; new=save_image(request.files.get("image"))
        if new: c.image=new
        db.session.commit();
        if new: remove_image(old)
        flash("Category updated successfully.","success"); return redirect(url_for("admin.admin_categories"))
    return render_template("front/admin/categories/edit.html", category=c)

@admin_bp.route("/categories/delete/<int:id>",methods=["POST"])
@admin_required
def delete_category(id):
    c=Category.query.get_or_404(id)
    if c.products:
        flash("Cannot delete a category that still has products.","danger"); return redirect(url_for("admin.admin_categories"))
    old=c.image; db.session.delete(c); db.session.commit(); remove_image(old); flash("Category deleted successfully.","success"); return redirect(url_for("admin.admin_categories"))
