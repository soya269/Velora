import os, uuid
from decimal import Decimal, InvalidOperation
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from extensions import db, limiter
from models import Product, ProductImage, Category, Brand
from . import admin_bp
from .auth import admin_required

ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}

def save_file(file, prefix="product"):
    if not file or not file.filename: return None
    safe = secure_filename(file.filename)
    if "." not in safe or safe.rsplit(".", 1)[1].lower() not in ALLOWED: return None
    ext = safe.rsplit(".", 1)[1].lower()
    name = f"{prefix}_{uuid.uuid4().hex}.{ext}"
    folder = current_app.config["PRODUCT_UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, name))
    return name

def remove_file(name):
    if not name or name.startswith(("http://", "https://")): return
    path = os.path.join(current_app.config["PRODUCT_UPLOAD_FOLDER"], name)
    if os.path.isfile(path): os.remove(path)

def decimal_value(value):
    try:
        result = Decimal(str(value or "0"))
        if result < 0: raise ValueError
        return result
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Cost and price must be valid non-negative numbers.")

def form_options():
    return (Category.query.order_by(Category.name.asc()).all(),
            Brand.query.order_by(Brand.name.asc()).all())

@admin_bp.route("/products")
@admin_required
def admin_products():
    return render_template("front/admin/products/index.html",
        products=Product.query.order_by(Product.id.desc()).all())

@admin_bp.route("/products/create", methods=["GET", "POST"])
@admin_required
@limiter.limit("60 per minute")
def create_product():
    categories, brands = form_options()
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            category_id = int(request.form.get("category_id", "0"))
            brand_raw = request.form.get("brand_id", "").strip()
            brand_id = int(brand_raw) if brand_raw else None
            cost = decimal_value(request.form.get("cost"))
            price = decimal_value(request.form.get("price"))
            stock = int(request.form.get("stock", "0"))
            rating = Decimal(str(request.form.get("rating", "0") or "0"))
            if rating < 0 or rating > 5: raise ValueError("Rating must be between 0 and 5.")
            if not name or not Category.query.get(category_id): raise ValueError("Choose a valid category and enter a product name.")
            if stock < 0: raise ValueError("Stock cannot be negative.")
            if brand_id and not Brand.query.get(brand_id): raise ValueError("Choose a valid brand.")
            thumb = save_file(request.files.get("thumbnail"))
            product = Product(name=name, thumbnail=thumb, cost=cost, price=price, stock=stock,
                              category_id=category_id, brand_id=brand_id, rating=rating,
                              description=request.form.get("description", "").strip())
            db.session.add(product); db.session.flush()
            if thumb: db.session.add(ProductImage(product_id=product.id, name=thumb))
            for file in request.files.getlist("images"):
                saved = save_file(file, "product_image")
                if saved: db.session.add(ProductImage(product_id=product.id, name=saved))
            db.session.commit()
            flash("Product created successfully.", "success")
            return redirect(url_for("admin.admin_products"))
        except Exception as exc:
            db.session.rollback()
            flash(str(exc) or "Could not create product.", "danger")
    return render_template("front/admin/products/create.html", categories=categories, brands=brands)

@admin_bp.route("/products/edit/<int:id>", methods=["GET", "POST"])
@admin_required
@limiter.limit("60 per minute")
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories, brands = form_options()
    if request.method == "POST":
        new_files = []
        try:
            name = request.form.get("name", "").strip()
            category_id = int(request.form.get("category_id", "0"))
            brand_raw = request.form.get("brand_id", "").strip()
            brand_id = int(brand_raw) if brand_raw else None
            cost = decimal_value(request.form.get("cost"))
            price = decimal_value(request.form.get("price"))
            stock = int(request.form.get("stock", "0"))
            rating = Decimal(str(request.form.get("rating", "0") or "0"))
            if rating < 0 or rating > 5: raise ValueError("Rating must be between 0 and 5.")
            if not name or not Category.query.get(category_id): raise ValueError("Choose a valid category and enter a product name.")
            if stock < 0: raise ValueError("Stock cannot be negative.")
            if brand_id and not Brand.query.get(brand_id): raise ValueError("Choose a valid brand.")
            product.name, product.category_id, product.brand_id = name, category_id, brand_id
            product.cost, product.price, product.stock, product.rating = cost, price, stock, rating
            product.description = request.form.get("description", "").strip()
            old_thumb = product.thumbnail
            new_thumb = save_file(request.files.get("thumbnail"))
            if new_thumb:
                new_files.append(new_thumb); product.thumbnail = new_thumb
                if not any(i.name == new_thumb for i in product.images):
                    db.session.add(ProductImage(product_id=product.id, name=new_thumb))
            for file in request.files.getlist("images"):
                saved = save_file(file, "product_image")
                if saved:
                    new_files.append(saved); db.session.add(ProductImage(product_id=product.id, name=saved))
            db.session.commit()
            if new_thumb: remove_file(old_thumb)
            flash("Product updated successfully.", "success")
            return redirect(url_for("admin.admin_products"))
        except Exception as exc:
            db.session.rollback()
            for filename in new_files: remove_file(filename)
            flash(str(exc) or "Could not update product.", "danger")
    return render_template("front/admin/products/edit.html", product=product, categories=categories, brands=brands)

@admin_bp.route("/products/delete/<int:id>", methods=["POST"])
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    filenames = {product.thumbnail} | {image.name for image in product.images}
    try:
        db.session.delete(product); db.session.commit()
        for filename in filenames: remove_file(filename)
        flash("Product deleted successfully.", "success")
    except Exception:
        db.session.rollback(); flash("Could not delete product.", "danger")
    return redirect(url_for("admin.admin_products"))
