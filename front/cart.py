
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from . import front_bp
from .store_utils import product_card

from extensions import db, limiter
from models import Product


# =====================================================
# GET CART
# Cart format: {"1": 2, "3": 1}
# =====================================================

def get_cart():
    cart = session.get("cart", {})
    valid = []

    # Convert old list format to dictionary format
    if isinstance(cart, list):
        converted_cart = {}

        for item in cart:
            if not isinstance(item, dict):
                continue

            try:
                product_id = str(int(item.get("id")))
                quantity = max(
                    1,
                    int(item.get("quantity", item.get("qty", 1)))
                )
                converted_cart[product_id] = (
                    converted_cart.get(product_id, 0) + quantity
                )
            except (TypeError, ValueError):
                continue

        cart = converted_cart

    if not isinstance(cart, dict):
        cart = {}

    clean_cart = {}

    for product_id, quantity in cart.items():
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        product = db.session.get(Product, product_id)

        if not product:
            continue

        stock = int(product.stock or 0)

        if stock <= 0:
            continue

        quantity = max(1, min(quantity, stock))

        card = product_card(product)

        card["quantity"] = quantity
        card["qty"] = quantity
        card["item_total"] = float(card["price"]) * quantity

        valid.append(card)

        clean_cart[str(product_id)] = quantity

    session["cart"] = clean_cart
    session.modified = True

    return valid


# =====================================================
# CALCULATE TOTALS
# =====================================================

def totals(items):
    subtotal = sum(
        float(item["price"]) * int(item["quantity"])
        for item in items
    )

    shipping = (
        float(current_app.config.get("SHIPPING_COST", 15))
        if subtotal > 0 else 0
    )

    tax = subtotal * float(
        current_app.config.get("TAX_RATE", 0.05)
    )

    total = subtotal + shipping + tax

    return subtotal, shipping, tax, total


# =====================================================
# CART PAGE
# =====================================================

@front_bp.route("/cart", methods=["GET"])
def cart():
    items = get_cart()

    subtotal, shipping, tax, total = totals(items)

    return render_template(
        "front/front/cart.html",
        cart_products=items,
        items=items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        total=total
    )


# =====================================================
# ADD TO CART
# Supports:
# POST /cart/add
# POST /cart/add/<product_id>
# =====================================================

@front_bp.route("/cart/add", methods=["POST"])
@front_bp.route("/cart/add/<int:product_id>", methods=["POST"])
@limiter.limit("120 per minute")
def add_to_cart(product_id=None):

    if product_id is None:
        product_id = request.form.get("product_id", type=int)

    if not product_id:
        flash("Please select a product.", "danger")
        return redirect(url_for("front.cart"))

    product = db.session.get(Product, product_id)

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("front.cart"))

    try:
        quantity = int(request.form.get("qty", 1))
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(1, quantity)

    stock = int(product.stock or 0)

    if stock <= 0:
        flash("This product is out of stock.", "warning")
        return redirect(url_for("front.cart"))

    cart = session.get("cart", {})

    # Convert old list format if necessary
    if isinstance(cart, list):
        converted = {}

        for item in cart:
            if isinstance(item, dict):
                try:
                    key = str(int(item.get("id")))
                    qty = int(item.get("quantity", item.get("qty", 1)))
                    converted[key] = converted.get(key, 0) + max(1, qty)
                except (TypeError, ValueError):
                    continue

        cart = converted

    if not isinstance(cart, dict):
        cart = {}

    key = str(product.id)
    current_qty = int(cart.get(key, 0))
    new_qty = current_qty + quantity

    if new_qty > stock:
        new_qty = stock
        flash("Maximum available stock reached.", "warning")
    else:
        flash("Product added to cart.", "success")

    cart[key] = new_qty

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("front.cart"))


# =====================================================
# UPDATE CART QUANTITY
# =====================================================

@front_bp.route("/cart/update/<int:product_id>", methods=["POST"])
@limiter.limit("120 per minute")
def update_cart(product_id):

    product = db.session.get(Product, product_id)

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("front.cart"))

    try:
        quantity = int(request.form.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    cart = session.get("cart", {})

    if not isinstance(cart, dict):
        cart = {}

    key = str(product_id)

    if quantity <= 0:
        cart.pop(key, None)
        flash("Product removed from cart.", "success")
    else:
        stock = int(product.stock or 0)

        if stock <= 0:
            cart.pop(key, None)
            flash("This product is out of stock.", "warning")
        else:
            cart[key] = min(quantity, stock)
            flash("Cart updated.", "success")

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("front.cart"))


# =====================================================
# INCREASE QUANTITY
# =====================================================

@front_bp.route("/cart/increase/<int:product_id>", methods=["POST"])
@limiter.limit("120 per minute")
def increase_cart(product_id):

    product = db.session.get(Product, product_id)

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("front.cart"))

    stock = int(product.stock or 0)

    if stock <= 0:
        flash("This product is out of stock.", "warning")
        return redirect(url_for("front.cart"))

    cart = session.get("cart", {})

    if not isinstance(cart, dict):
        cart = {}

    key = str(product_id)
    current_qty = int(cart.get(key, 0))

    if current_qty >= stock:
        flash("Maximum available stock reached.", "warning")
    else:
        cart[key] = current_qty + 1
        flash("Quantity increased.", "success")

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("front.cart"))


# =====================================================
# DECREASE QUANTITY
# =====================================================

@front_bp.route("/cart/decrease/<int:product_id>", methods=["POST"])
@limiter.limit("120 per minute")
def decrease_cart(product_id):

    cart = session.get("cart", {})

    if not isinstance(cart, dict):
        cart = {}

    key = str(product_id)
    current_qty = int(cart.get(key, 0))

    if current_qty <= 1:
        cart.pop(key, None)
        flash("Product removed from cart.", "info")
    else:
        cart[key] = current_qty - 1
        flash("Quantity decreased.", "success")

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("front.cart"))


# =====================================================
# REMOVE PRODUCT
# =====================================================

@front_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
@limiter.limit("120 per minute")
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    if not isinstance(cart, dict):
        cart = {}

    cart.pop(str(product_id), None)

    session["cart"] = cart
    session.modified = True

    flash("Product removed from cart.", "success")

    return redirect(url_for("front.cart"))


# =====================================================
# CLEAR ENTIRE CART
# =====================================================

@front_bp.route("/cart/clear", methods=["POST"])
def clear_cart():

    session["cart"] = {}
    session.modified = True

    flash("Your cart has been cleared.", "success")

    return redirect(url_for("front.cart"))
