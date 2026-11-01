
from flask import render_template, request
from . import front_bp
from .store_utils import product_card
from models import Product, Category, Brand


# ==========================================
# HOME PAGE
# ==========================================

@front_bp.route("/")
def home():
    products = [
        product_card(p)
        for p in Product.query.order_by(
            Product.id.desc()
        ).limit(12).all()
    ]

    categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    return render_template(
        "front/front/index.html",
        products=products,
        categories=categories
    )


# ==========================================
# ABOUT PAGE
# ==========================================

@front_bp.route("/about")
def about():
    products = [
        product_card(p)
        for p in Product.query.order_by(
            Product.id.desc()
        ).limit(4).all()
    ]

    return render_template(
        "front/front/about.html",
        products=products
    )


# ==========================================
# CONTACT PAGE
# ==========================================

@front_bp.route("/contact")
def contact():
    return render_template("front/front/contact.html")


# ==========================================
# SHOP PAGE - ALL PRODUCTS
# No search or filters
# ==========================================

@front_bp.route("/shop")
def shop():
    rows = Product.query.order_by(
        Product.id.desc()
    ).all()

    products = [product_card(p) for p in rows]

    return render_template(
        "front/front/shop.html",
        products=products
    )


# ==========================================
# PRODUCTS / COLLECTION PAGE
# Search, Category and Stock filters
# ==========================================

@front_bp.route("/products")
def product_list():
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    in_stock = request.args.get("in_stock")

    query = Product.query

    if q:
        query = query.filter(
            Product.name.ilike(f"%{q}%")
        )

    if category_id:
        query = query.filter(
            Product.category_id == category_id
        )

    if in_stock == "1":
        query = query.filter(
            Product.stock > 0
        )

    rows = query.order_by(Product.id.desc()).all()

    products = [product_card(p) for p in rows]

    return render_template(
        "front/front/products.html",
        products=products,
        categories=Category.query.order_by(
            Category.name.asc()
        ).all(),
        search=q,
        in_stock=in_stock
    )


# ==========================================
# PRODUCTS BY CATEGORY
# ==========================================

@front_bp.route("/products/category/<string:category_name>")
def product_category(category_name):

    # Find category by name (case-insensitive)
    category = Category.query.filter(
        Category.name.ilike(category_name)
    ).first_or_404()

    # Get products belonging to the selected category
    rows = Product.query.filter_by(
        category_id=category.id
    ).order_by(
        Product.id.desc()
    ).all()

    # Format product data
    products = [product_card(p) for p in rows]

    # Get categories in alphabetical order (A-Z)
    categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    # Get brands
    brands = Brand.query.order_by(
        Brand.name.asc()
    ).all()

    return render_template(
        "front/front/products.html",
        products=products,
        categories=categories,
        brands=brands,
        selected_category=category.name,
        current_category=category.name,
        search="",
        in_stock=""
    )


# ==========================================
# PRODUCT DETAIL
# ==========================================

@front_bp.route("/products/<int:id>")
@front_bp.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)

    from .store_utils import related_products

    return render_template(
        "front/front/product_detail.html",
        product=product_card(product),
        related_products=related_products(product)
    )

