from flask import url_for
from models import Product

def image_path(name):
    if not name: return ""
    if name.startswith(("http://", "https://", "/static/")): return name
    return url_for("static", filename="uploads/products/" + name)

def product_card(product):
    images = [image_path(i.name) for i in product.images]
    main = image_path(product.thumbnail) if product.thumbnail else (images[0] if images else "")
    if main and main not in images: images.insert(0, main)
    return {
        "id": product.id, "title": product.name, "name": product.name,
        "price": float(product.price or 0), "cost": float(product.cost or 0),
        "stock": product.stock, "rating": float(product.rating or 0), "thumbnail": main, "image": main,
        "images": images, "description": product.description or "",
        "category": {"id": product.category_id, "name": product.category.name if product.category else "Uncategorized"},
        "brand": {"id": product.brand_id, "name": product.brand.name if product.brand else "No brand"},
        "category_name": product.category.name if product.category else "Uncategorized",
        "brand_name": product.brand.name if product.brand else "No brand"
    }

def related_products(product, limit=4):
    q = Product.query.filter(Product.id != product.id)
    if product.category_id: q = q.filter(Product.category_id == product.category_id)
    return [product_card(p) for p in q.order_by(Product.id.desc()).limit(limit).all()]
