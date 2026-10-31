from flask import render_template, request
from . import front_bp
from .store_utils import product_card
from models import Product, Category, Brand

@front_bp.route("/")
def home():
    products = [product_card(p) for p in Product.query.order_by(Product.id.desc()).limit(12).all()]
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("front/front/index.html", products=products, categories=categories)

@front_bp.route("/about")
def about():
    products = [product_card(p) for p in Product.query.order_by(Product.id.desc()).limit(4).all()]
    return render_template("front/front/about.html", products=products)

@front_bp.route("/contact")
def contact():
    return render_template("front/front/contact.html")

@front_bp.route("/shop")
def shop():
    return product_list()

@front_bp.route("/products")
def product_list():
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    brand_id = request.args.get("brand", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    in_stock = request.args.get("in_stock")
    query = Product.query
    if q: query = query.filter(Product.name.ilike(f"%{q}%"))
    if category_id: query = query.filter(Product.category_id == category_id)
    if brand_id: query = query.filter(Product.brand_id == brand_id)
    if min_price is not None: query = query.filter(Product.price >= min_price)
    if max_price is not None: query = query.filter(Product.price <= max_price)
    if in_stock == "1": query = query.filter(Product.stock > 0)
    rows = query.order_by(Product.id.desc()).all()
    products = [product_card(p) for p in rows]
    return render_template("front/front/products.html", products=products,
        categories=Category.query.order_by(Category.name.asc()).all(),
        brands=Brand.query.order_by(Brand.name.asc()).all(),
        selected_category="All Products", current_category="All Products",
        search=q, selected_brand=brand_id, min_price=request.args.get("min_price",""),
        max_price=request.args.get("max_price",""), in_stock=in_stock)

@front_bp.route("/products/category/<category_name>")
def product_category(category_name):
    category = Category.query.filter(Category.name.ilike(category_name)).first_or_404()
    products = [product_card(p) for p in Product.query.filter_by(category_id=category.id).all()]
    return render_template("front/front/products.html", products=products,
        categories=Category.query.all(), brands=Brand.query.all(),
        selected_category=category.name, current_category=category.name, search="")

@front_bp.route("/products/<int:id>")
@front_bp.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)
    from .store_utils import related_products
    return render_template("front/front/product_detail.html",
        product=product_card(product), related_products=related_products(product))
