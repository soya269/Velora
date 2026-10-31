from flask import Blueprint, jsonify, request
from models import Product, Category, Brand

core_bp = Blueprint("core", __name__, url_prefix="/api/core")

def product_json(p):
    images = [i.name for i in p.images]
    return {
        "id": p.id, "name": p.name, "title": p.name,
        "thumbnail": p.thumbnail, "images": images,
        "cost": float(p.cost or 0), "price": float(p.price or 0),
        "stock": p.stock, "category_id": p.category_id,
        "category_name": p.category.name if p.category else None,
        "brand_id": p.brand_id, "brand_name": p.brand.name if p.brand else None,
        "description": p.description or "", "rating": float(p.rating or 0), "images_count": len(images)
    }

@core_bp.route("/products", methods=["GET"])
def get_products():
    query = Product.query
    category_id = request.args.get("category", type=int)
    brand_id = request.args.get("brand", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    in_stock = request.args.get("in_stock")
    if category_id: query = query.filter(Product.category_id == category_id)
    if brand_id: query = query.filter(Product.brand_id == brand_id)
    if min_price is not None: query = query.filter(Product.price >= min_price)
    if max_price is not None: query = query.filter(Product.price <= max_price)
    if in_stock == "1": query = query.filter(Product.stock > 0)
    rows = query.order_by(Product.id.desc()).all()
    data = [product_json(p) for p in rows]
    return jsonify({"success": True, "total": len(data), "data": data})

@core_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({"success": True, "data": product_json(p)})

@core_bp.route("/categories", methods=["GET"])
def get_categories():
    rows = Category.query.order_by(Category.name.asc()).all()
    return jsonify({"success": True, "data": [{"id":c.id,"name":c.name,"image":c.image,"description":c.description} for c in rows]})

@core_bp.route("/brands", methods=["GET"])
def get_brands():
    rows = Brand.query.order_by(Brand.name.asc()).all()
    return jsonify({"success": True, "data": [{"id":b.id,"name":b.name,"image":b.image,"description":b.description} for b in rows]})
