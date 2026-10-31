from flask import jsonify
from models import Category, Product
from . import api_bp


@api_bp.route("/categories", methods=["GET"])
def categories():
    return jsonify({"success": True,
                    "categories": [{"id": c.id, "name": c.name, "image": c.image, "description": c.description} for c in
                                   Category.query.all()]})

@api_bp.route("/products", methods=["GET"])
def products():
    rows = Product.query.order_by(Product.id.desc()).all()
    return jsonify({"success": True, "products": [
        {"id": p.id, "name": p.name, "thumbnail": p.thumbnail, "cost": float(p.cost or 0), "price": float(p.price or 0),
         "stock": p.stock, "category_id": p.category_id, "category": p.category.name, "description": p.description,
         "images": [i.name for i in p.images]} for p in rows]})
@api_bp.route("/products/<int:product_id>", methods=["GET"])
def product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({"success": True,
                    "product": {"id": p.id, "name": p.name, "thumbnail": p.thumbnail, "cost": float(p.cost or 0),
                                "price": float(p.price or 0), "stock": p.stock, "category_id": p.category_id,
                                "category": p.category.name, "description": p.description,
                                "images": [i.name for i in p.images]}})
@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"success": True, "service": "VELORA API", "status": "ok"})
