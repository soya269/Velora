
import urllib.parse
import urllib.request

from uuid import uuid4

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from . import front_bp
from extensions import db, limiter
from models import Order, OrderItem, Product
from .cart import get_cart, totals
import os
import requests
from html import escape

# ==========================================
# TELEGRAM ORDER NOTIFICATION
# ==========================================
def send_telegram_order(
    order,
    order_items,
    payment_method,
    subtotal,
    shipping,
    tax
):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    timeout = int(os.getenv("TELEGRAM_TIMEOUT", "15"))

    if not bot_token or not chat_id:
        print("Telegram ERROR: Missing bot token or chat ID.")
        return False

    # ------------------------------------------
    # PAYMENT METHOD
    # ------------------------------------------
    payment_labels = {
        "cod": "Cash on Delivery (COD)",
        "khqr": "KHQR Payment"
    }

    payment_text = payment_labels.get(
        payment_method.lower(),
        payment_method.upper()
    )

    # ------------------------------------------
    # ORDER ITEMS
    # ------------------------------------------
    product_lines = []

    for item in order_items:

        product_name = escape(str(item["title"]))
        quantity = int(item["quantity"])
        price = float(item["price"])
        item_total = price * quantity

        product_lines.append(
            f"• {product_name}\n"
            f"  {quantity} x ${price:.2f} = ${item_total:.2f}"
        )

    items_text = "\n".join(product_lines)

    # ------------------------------------------
    # CUSTOMER INFORMATION
    # ------------------------------------------
    customer_name = escape(str(order.customer_name or "N/A"))
    phone = escape(str(order.phone or "N/A"))
    address = escape(str(order.address or "N/A"))

    order_id = order.id
    order_ref = escape(str(order.order_ref or "N/A"))
    status = escape(str(order.status or "Pending Payment"))

    # ------------------------------------------
    # TOTALS
    # ------------------------------------------
    subtotal = float(subtotal)
    shipping = float(shipping)
    tax = float(tax)
    total = float(order.total)

    # ------------------------------------------
    # TELEGRAM MESSAGE
    # ------------------------------------------
    message = (
        "🛍️ <b>NEW VELORA ORDER</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "📦 <b>ORDER INFORMATION</b>\n"
        f"Order ID: #{order_id}\n"
        f"Order Ref: <code>{order_ref}</code>\n"
        f"Status: <b>{status}</b>\n\n"

        "👤 <b>CUSTOMER INFORMATION</b>\n"
        f"Name: {customer_name}\n"
        f"Phone: {phone}\n"
        f"Address: {address}\n\n"

        "💳 <b>PAYMENT METHOD</b>\n"
        f"{escape(payment_text)}\n\n"

        "🛒 <b>ORDER ITEMS</b>\n"
        f"{items_text}\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>PAYMENT SUMMARY</b>\n"
        f"Subtotal: ${subtotal:.2f}\n"
        f"Shipping: ${shipping:.2f}\n"
        f"Tax: ${tax:.2f}\n"
        f"Total: <b>${total:.2f}</b>\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "Thank you for choosing VELORA ❤️"
    )

    # ------------------------------------------
    # SEND TO TELEGRAM
    # ------------------------------------------
    telegram_url = (
        f"https://api.telegram.org/bot{bot_token}/sendMessage"
    )

    try:
        response = requests.post(
            telegram_url,
            data={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=timeout
        )

        result = response.json()

        if response.ok and result.get("ok"):
            print(
                f"Telegram notification sent for order #{order_id}"
            )
            return True

        print("Telegram API ERROR:", result)
        return False

    except (requests.RequestException, ValueError) as error:
        print("Telegram sending ERROR:", error)
        return False
# ==========================================
# CHECKOUT PAGE - GET
# URL: /checkout
# ==========================================
@front_bp.route("/checkout", methods=["GET", "POST"])
@limiter.limit("30 per minute")
def checkout():

    # ==========================================
    # 1. CHECK USER LOGIN
    # ==========================================
    if "user" not in session:
        flash("Please login before checkout.", "warning")
        return redirect(url_for("front.login"))

    items = []
    checkout_mode = "cart"

    # ==========================================
    # 2. BUY NOW - DIRECT CHECKOUT
    # ==========================================
    if request.method == "POST":

        product_id = request.form.get("product_id", type=int)
        quantity = request.form.get("qty", default=1, type=int)

        # Validate input
        if not product_id or not quantity or quantity < 1:
            flash("Invalid product or quantity.", "warning")
            return redirect(url_for("front.product_list"))

        # Find product
        product = db.session.get(Product, product_id)

        if product is None:
            flash("Product not found.", "danger")
            return redirect(url_for("front.product_list"))

        # Check available stock
        if product.stock is None or product.stock < quantity:
            flash(
                f"Only {product.stock or 0} item(s) are available.",
                "warning"
            )
            return redirect(
                request.referrer or url_for("front.product_list")
            )

        # Get product image
        product_image = product.thumbnail or ""

        if not product_image and product.images:
            product_image = product.images[0].name or ""

        # Prepare direct checkout item
        items = [{
            "id": product.id,
            "title": product.name,
            "name": product.name,
            "price": float(product.price),
            "qty": quantity,
            "quantity": quantity,
            "image": product_image,
            "item_total": float(product.price) * quantity,
            "description": product.description or ""
        }]

        checkout_mode = "direct"

        # Save direct checkout information
        # This does not modify the shopping cart.
        session["checkout_data"] = {
            "mode": "direct",
            "product_id": product.id,
            "quantity": quantity
        }

        # Generate a new order reference for this purchase
        order_ref = "VEL-" + uuid4().hex[:10].upper()
        session["checkout_order_ref"] = order_ref

    # ==========================================
    # 3. GET CHECKOUT - CART OR EXISTING BUY NOW
    # ==========================================
    else:

        checkout_data = session.get("checkout_data", {})

        # --------------------------------------
        # Continue existing Buy Now checkout
        # --------------------------------------
        if checkout_data.get("mode") == "direct":

            product_id = checkout_data.get("product_id")
            quantity = checkout_data.get("quantity", 1)

            product = (
                db.session.get(Product, product_id)
                if product_id else None
            )

            if (
                product is None
                or quantity < 1
                or product.stock is None
                or product.stock < quantity
            ):
                session.pop("checkout_data", None)
                session.pop("checkout_order_ref", None)

                flash(
                    "The selected product is unavailable or out of stock.",
                    "warning"
                )
                return redirect(url_for("front.product_list"))

            # Get product image
            product_image = product.thumbnail or ""

            if not product_image and product.images:
                product_image = product.images[0].name or ""

            items = [{
                "id": product.id,
                "title": product.name,
                "name": product.name,
                "price": float(product.price),
                "qty": quantity,
                "quantity": quantity,
                "image": product_image,
                "item_total": float(product.price) * quantity,
                "description": product.description or ""
            }]

            checkout_mode = "direct"

        # --------------------------------------
        # Normal Cart Checkout
        # --------------------------------------
        else:

            items = get_cart()

            if not items:
                flash(
                    "Your cart is empty. Please add products first.",
                    "warning"
                )
                return redirect(url_for("front.cart"))

            checkout_mode = "cart"

            session["checkout_data"] = {
                "mode": "cart"
            }

        # Reuse existing order reference
        order_ref = session.get("checkout_order_ref")

        if not order_ref:
            order_ref = "VEL-" + uuid4().hex[:10].upper()
            session["checkout_order_ref"] = order_ref

    # ==========================================
    # 4. CALCULATE TOTALS
    # ==========================================
    subtotal, shipping, tax, total = totals(items)

    # ==========================================
    # 5. GENERATE DEMO QR CODE
    # ==========================================
    qr_payload = (
        f"VELORA ORDER:{order_ref}; AMOUNT:{total:.2f} USD"
    )

    qr_url = (
        "https://api.qrserver.com/v1/create-qr-code/"
        "?size=220x220&data="
        + urllib.parse.quote(qr_payload)
    )

    # ==========================================
    # 6. DISPLAY CHECKOUT PAGE
    # ==========================================
    return render_template(
        "front/front/checkout.html",
        cart_products=items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        total=total,
        order_ref=order_ref,
        qr_url=qr_url,
        checkout_mode=checkout_mode,
        user=session["user"]
    )

# ==========================================
# BUY NOW - DIRECT CHECKOUT
# URL: /buy-now/<product_id>
# ==========================================

@front_bp.route("/buy-now/<int:product_id>", methods=["POST"])
@limiter.limit("30 per minute")
def buy_now(product_id):

    if "user" not in session:
        flash("Please login before buying.", "warning")
        return redirect(url_for("front.login"))

    # Find product
    product = db.session.get(Product, product_id)

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("front.home"))

    # Get selected quantity
    try:
        quantity = int(
            request.form.get(
                "quantity",
                request.form.get("qty", 1)
            )
        )
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        flash("Please select a valid quantity.", "warning")
        return redirect(
            url_for("front.product_detail", product_id=product.id)
        )

    # Check available stock
    if not product.stock or quantity > product.stock:
        flash(
            f"Only {product.stock} unit(s) are available.",
            "warning"
        )
        return redirect(
            url_for("front.product_detail", product_id=product.id)
        )

    # Replace cart with this product only
    session["cart"] = {
        str(product.id): quantity
    }

    # Generate a fresh checkout reference
    session.pop("checkout_order_ref", None)

    session.modified = True

    flash("Product added. Please complete your checkout.", "success")

    return redirect(url_for("front.checkout"))

# ==========================================
# PLACE ORDER - POST
# URL: /place-order
# ==========================================
@front_bp.route("/place-order", methods=["POST"])
@limiter.limit("30 per minute")
def place_order():

    if "user" not in session:
        flash("Please login before checkout.", "warning")
        return redirect(url_for("front.login"))

    # ------------------------------------------
    # IDENTIFY CHECKOUT MODE
    # ------------------------------------------
    checkout_data = session.get("checkout_data", {})
    checkout_mode = checkout_data.get("mode", "cart")

    items = []

    # ------------------------------------------
    # BUY NOW: GET THE SELECTED PRODUCT
    # ------------------------------------------
    if checkout_mode == "direct":

        product_id = checkout_data.get("product_id")
        quantity = checkout_data.get("quantity")

        if not product_id or not quantity:
            flash("Your direct checkout session has expired.", "warning")
            return redirect(url_for("front.product_list"))

        product = db.session.get(Product, int(product_id))

        if not product:
            flash("Product not found.", "danger")
            return redirect(url_for("front.product_list"))

        quantity = int(quantity)

        if quantity < 1 or product.stock < quantity:
            flash(
                f"Insufficient stock for {product.name}. "
                f"Available: {product.stock}.",
                "warning"
            )
            return redirect(url_for("front.product_list"))

        items = [{
            "id": product.id,
            "title": product.name,
            "name": product.name,
            "price": float(product.price),
            "qty": quantity,
            "quantity": quantity,
            "item_total": float(product.price) * quantity
        }]

    # ------------------------------------------
    # NORMAL CART CHECKOUT
    # ------------------------------------------
    elif checkout_mode == "cart":

        items = get_cart()

        if not items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for("front.cart"))

    else:
        flash("Invalid checkout session. Please try again.", "danger")
        return redirect(url_for("front.product_list"))

    # ------------------------------------------
    # CUSTOMER INFORMATION
    # ------------------------------------------
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    payment_method = (
        request.form.get("payment_method", "cod").strip().lower()
    )

    if not all([name, phone, address]):
        flash(
            "Please complete your name, phone number, and address.",
            "danger"
        )
        return redirect(url_for("front.checkout"))

    if payment_method not in ["cod", "khqr"]:
        flash("Invalid payment method.", "danger")
        return redirect(url_for("front.checkout"))

    # ------------------------------------------
    # RECHECK PRODUCTS AND STOCK
    # ------------------------------------------
    telegram_items = []
    verified_items = []

    try:
        for item in items:

            product_id = int(item["id"])
            quantity = int(item.get("quantity", item.get("qty", 0)))

            product = db.session.get(Product, product_id)

            if not product:
                raise ValueError("A product no longer exists.")

            if quantity < 1:
                raise ValueError(f"Invalid quantity for {product.name}.")

            if product.stock < quantity:
                raise ValueError(
                    f"Only {product.stock} unit(s) of "
                    f"{product.name} are available."
                )

            price = float(product.price)

            verified_items.append({
                "product": product,
                "quantity": quantity,
                "price": price
            })

            telegram_items.append({
                "title": product.name,
                "price": price,
                "quantity": quantity
            })

        # Calculate using verified database products.
        total_items = [{
            "id": entry["product"].id,
            "title": entry["product"].name,
            "name": entry["product"].name,
            "price": entry["price"],
            "qty": entry["quantity"],
            "quantity": entry["quantity"],
            "item_total": entry["price"] * entry["quantity"]
        } for entry in verified_items]

        subtotal, shipping, tax, total = totals(total_items)

        order_ref = (
            session.get("checkout_order_ref")
            or "VEL-" + uuid4().hex[:10].upper()
        )

        order = Order(
            order_ref=order_ref,
            user_id=session["user"]["id"],
            customer_name=name,
            phone=phone,
            address=address,
            total=total,
            status="Pending Payment"
        )

        db.session.add(order)

        for entry in verified_items:

            product = entry["product"]
            quantity = entry["quantity"]

            order_item = OrderItem(
                order=order,
                product_id=product.id,
                title=product.name,
                price=entry["price"],
                quantity=quantity
            )

            db.session.add(order_item)

            # Update stock
            product.stock -= quantity

        # Commit order, order items, and stock together.
        db.session.commit()

    except Exception as error:
        db.session.rollback()

        print("PLACE ORDER ERROR:", error)

        flash(
            f"Could not place your order: {error}",
            "danger"
        )
        return redirect(url_for("front.checkout"))

    # ------------------------------------------
    # SEND TELEGRAM AFTER SUCCESSFUL COMMIT
    # ------------------------------------------
    telegram_sent = send_telegram_order(
        order=order,
        order_items=telegram_items,
        payment_method=payment_method,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax
    )

    if not telegram_sent:
        print(
            f"WARNING: Order {order.order_ref} was saved, "
            "but Telegram notification was not sent."
        )

    # ------------------------------------------
    # CLEAR CART ONLY FOR CART CHECKOUT
    # ------------------------------------------
    if checkout_mode == "cart":
        session["cart"] = {}

    # Buy Now does not change the existing cart.
    session.pop("checkout_data", None)
    session.pop("checkout_order_ref", None)

    session["last_order_id"] = order.id
    session.modified = True

    if telegram_sent:
        flash("Your order was placed successfully!", "success")
    else:
        flash(
            "Your order was saved, but the Telegram notification failed.",
            "warning"
        )

    return redirect(
        url_for("front.order_success", order_id=order.id)
    )

@front_bp.route(
    "/order/success/<int:order_id>",
    methods=["GET"]
)
def order_success(order_id):

    order = db.session.get(Order, order_id)

    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("front.home"))

    if (
        "user" not in session
        or order.user_id != session["user"]["id"]
    ):
        flash("Order not found.", "danger")
        return redirect(url_for("front.home"))

    return render_template(
        "front/front/order_success.html",
        order=order
    )
