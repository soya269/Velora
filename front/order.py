# # # from flask import render_template, request, redirect, url_for, session, flash
# # # from . import front_bp
# # # from extensions import db, limiter
# # # from models import Order, OrderItem
# # #
# # # @front_bp.route("/checkout", methods=["GET", "POST"])
# # import os
# # import json
# # import urllib.parse
# # import urllib.request
# #
# # from flask import (
# #     render_template,
# #     request,
# #     redirect,
# #     url_for,
# #     session,
# #     flash
# # )
# #
# # from . import front_bp
# # from extensions import db, limiter
# # from models import Order, OrderItem, Product
# # from .store_utils import product_card
# # from .cart import totals
# # @front_bp.route("/place-order", methods=["POST"])
# # @limiter.limit("30 per minute")
# # def checkout():
# #     from uuid import uuid4
# #     from models import Product
# #     from .store_utils import product_card
# #     from .cart import totals
# #
# #     if "user" not in session:
# #         flash("Please login before checkout.", "warning")
# #         return redirect(url_for("front.login"))
# #
# #     cart_rows = session.get("cart", [])
# #     items = []
# #     for row in cart_rows:
# #         product = Product.query.get(row.get("id"))
# #         if not product: continue
# #         qty = max(1, int(row.get("quantity", 1)))
# #         if qty > product.stock:
# #             flash(f"Only {product.stock} unit(s) of {product.name} are available.", "warning")
# #             qty = product.stock
# #         if qty:
# #             card = product_card(product)
# #             card.update({"quantity": qty, "qty": qty, "item_total": float(product.price) * qty})
# #             items.append(card)
# #     session["cart"] = [{"id":x["id"], "quantity":x["quantity"]} for x in items]
# #     if not items:
# #         flash("Your cart is empty or its products are unavailable.", "warning")
# #         return redirect(url_for("front.cart"))
# #
# #     subtotal, shipping, tax, total = totals(items)
# #     order_ref = session.get("checkout_order_ref") or ("VEL-" + uuid4().hex[:10].upper())
# #     session["checkout_order_ref"] = order_ref
# #     qr_payload = f"VELORA ORDER:{order_ref}; AMOUNT:{total:.2f} USD"
# #     qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=" + urllib.parse.quote(qr_payload)
# #
# #     if request.method == "POST":
# #         name = request.form.get("name", "").strip()
# #         if not name:
# #             name = " ".join(x for x in [request.form.get("first_name","").strip(),
# #                                          request.form.get("last_name","").strip()] if x)
# #         phone = request.form.get("phone", "").strip()
# #         address = request.form.get("address", "").strip()
# #         if not all([name, phone, address]):
# #             flash("Please complete your shipping information.", "danger")
# #             return redirect(url_for("front.checkout"))
# #
# #         order = Order(order_ref=order_ref, user_id=session["user"]["id"],
# #                       customer_name=name, phone=phone, address=address,
# #                       total=total, status="Pending Payment")
# #         try:
# #             db.session.add(order)
# #             for item in items:
# #                 product = Product.query.get(item["id"])
# #                 if not product or product.stock < item["quantity"]:
# #                     raise ValueError(f"Insufficient stock for {item['title']}.")
# #                 db.session.add(OrderItem(order=order, product_id=product.id,
# #                     title=product.name, price=float(product.price), quantity=item["quantity"]))
# #                 product.stock -= item["quantity"]
# #             db.session.commit()
# #             db.session.refresh(order)
# #         except Exception as exc:
# #             db.session.rollback()
# #             flash(str(exc) or "Could not create your order.", "danger")
# #             return redirect(url_for("front.cart"))
# #
# #         send_telegram_order(order)
# #         session["cart"] = []
# #         session.pop("checkout_order_ref", None)
# #         session["last_order_id"] = order.id
# #         return redirect(url_for("front.order_success", order_id=order.id))
# #
# #     return render_template("front/front/checkout.html", cart_items=items, cart_products=items,
# #         total=total, subtotal=subtotal, shipping=shipping, tax=tax, user=session["user"],
# #         order_ref=order_ref, qr_url=qr_url)
# #
# #
# # @front_bp.route("/order/success/<int:order_id>")
# # def order_success(order_id):
# #     order = Order.query.get_or_404(order_id)
# #     if "user" not in session or order.user_id != session["user"]["id"]:
# #         flash("Order not found.", "danger")
# #         return redirect(url_for("front.home"))
# #     return render_template("front/front/order_success.html", order=order)
#
# import os
# import urllib.parse
# import urllib.request
#
# from uuid import uuid4
#
# from flask import (
#     render_template,
#     request,
#     redirect,
#     url_for,
#     session,
#     flash
# )
#
# from . import front_bp
# from extensions import db, limiter
# from models import Order, OrderItem, Product
# from .store_utils import product_card
# from .cart import totals
#
#
# # ==========================================
# # TELEGRAM ORDER NOTIFICATION
# # ==========================================
#
# def send_telegram_order(order):
#     """Send an order notification if Telegram is configured."""
#
#     # Read credentials from environment variables
#     token = os.getenv("TELEGRAM_BOT_TOKEN")
#     chat_id = os.getenv("TELEGRAM_CHAT_ID")
#
#     if not token or not chat_id:
#         print("Telegram notification skipped: credentials not configured.")
#         return
#
#     message = (
#         "New VELORA Order\n"
#         f"Order: {order.order_ref}\n"
#         f"Customer: {order.customer_name}\n"
#         f"Phone: {order.phone}\n"
#         f"Total: ${float(order.total):.2f}\n"
#         f"Status: {order.status}"
#     )
#
#     url = f"https://api.telegram.org/bot{token}/sendMessage"
#
#     data = urllib.parse.urlencode({
#         "chat_id": chat_id,
#         "text": message
#     }).encode("utf-8")
#
#     try:
#         req = urllib.request.Request(url, data=data)
#
#         with urllib.request.urlopen(req, timeout=10) as response:
#             print("Telegram notification sent successfully.")
#
#     except Exception as error:
#         print(f"Telegram notification failed: {error}")
#
#
# # ==========================================
# # PLACE ORDER
# # ==========================================
#
# @front_bp.route("/place-order", methods=["POST"])
# @limiter.limit("30 per minute")
# def checkout():
#
#     if "user" not in session:
#         flash("Please login before checkout.", "warning")
#         return redirect(url_for("front.login"))
#
#     cart_rows = session.get("cart", [])
#
#     items = []
#
#     # Get products from database
#     for row in cart_rows:
#
#         product = Product.query.get(row.get("id"))
#
#         if not product:
#             continue
#
#         qty = max(1, int(row.get("quantity", 1)))
#
#         if qty > product.stock:
#             flash(
#                 f"Only {product.stock} unit(s) of "
#                 f"{product.name} are available.",
#                 "warning"
#             )
#             qty = product.stock
#
#         if qty > 0:
#             card = product_card(product)
#
#             card.update({
#                 "quantity": qty,
#                 "qty": qty,
#                 "item_total": float(product.price) * qty
#             })
#
#             items.append(card)
#
#     # Update cart session
#     session["cart"] = [
#         {
#             "id": item["id"],
#             "quantity": item["quantity"]
#         }
#         for item in items
#     ]
#
#     if not items:
#         flash(
#             "Your cart is empty or its products are unavailable.",
#             "warning"
#         )
#         return redirect(url_for("front.cart"))
#
#     # Calculate order totals
#     subtotal, shipping, tax, total = totals(items)
#
#     order_ref = (
#         session.get("checkout_order_ref")
#         or "VEL-" + uuid4().hex[:10].upper()
#     )
#
#     session["checkout_order_ref"] = order_ref
#
#     # Shipping information
#     name = request.form.get("name", "").strip()
#
#     if not name:
#         name = " ".join([
#             x for x in [
#                 request.form.get("first_name", "").strip(),
#                 request.form.get("last_name", "").strip()
#             ] if x
#         ])
#
#     phone = request.form.get("phone", "").strip()
#     address = request.form.get("address", "").strip()
#
#     if not all([name, phone, address]):
#         flash(
#             "Please complete your shipping information.",
#             "danger"
#         )
#         return redirect(url_for("front.checkout"))
#
#     # Create order
#     order = Order(
#         order_ref=order_ref,
#         user_id=session["user"]["id"],
#         customer_name=name,
#         phone=phone,
#         address=address,
#         total=total,
#         status="Pending Payment"
#     )
#
#     try:
#
#         db.session.add(order)
#
#         for item in items:
#
#             product = Product.query.get(item["id"])
#
#             if not product or product.stock < item["quantity"]:
#                 raise ValueError(
#                     f"Insufficient stock for {item['title']}."
#                 )
#
#             order_item = OrderItem(
#                 order=order,
#                 product_id=product.id,
#                 title=product.name,
#                 price=float(product.price),
#                 quantity=item["quantity"]
#             )
#
#             db.session.add(order_item)
#
#             # Reduce stock
#             product.stock -= item["quantity"]
#
#         db.session.commit()
#
#         db.session.refresh(order)
#
#     except Exception as error:
#
#         db.session.rollback()
#
#         flash(
#             str(error) or "Could not create your order.",
#             "danger"
#         )
#
#         return redirect(url_for("front.cart"))
#
#     # Send Telegram notification
#     send_telegram_order(order)
#
#     # Clear cart
#     session["cart"] = []
#     session.pop("checkout_order_ref", None)
#
#     session["last_order_id"] = order.id
#
#     return redirect(
#         url_for("front.order_success", order_id=order.id)
#     )
#
#
# # ==========================================
# # ORDER SUCCESS
# # ==========================================
#
# @front_bp.route("/order/success/<int:order_id>")
# def order_success(order_id):
#
#     order = Order.query.get_or_404(order_id)
#
#     if (
#         "user" not in session
#         or order.user_id != session["user"]["id"]
#     ):
#         flash("Order not found.", "danger")
#         return redirect(url_for("front.home"))
#
#     return render_template(
#         "front/front/order_success.html",
#         order=order
#     )

import os
import html
import json
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
    """
    Send detailed order information to Telegram.
    A Telegram error will not cancel the saved order.
    """

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram skipped: credentials are not configured.")
        return False

    def safe(value):
        return html.escape(str(value if value is not None else "-"))

    payment_names = {
        "cod": "Cash on Delivery (COD)",
        "khqr": "KHQR"
    }

    payment_name = payment_names.get(
        payment_method,
        payment_method.upper()
    )

    # Build product list using database product information
    product_lines = []

    for item in order_items:
        title = safe(item["title"])
        quantity = int(item["quantity"])
        price = float(item["price"])
        item_total = quantity * price

        product_lines.append(
            f"• {title}\n"
            f"  {quantity} x ${price:.2f} = ${item_total:.2f}"
        )

    products_text = "\n".join(product_lines)

    message = (
        "🛍️ <b>NEW VELORA ORDER</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "📦 <b>ORDER INFORMATION</b>\n"
        f"Order ID: #{order.id}\n"
        f"Order Ref: <code>{safe(order.order_ref)}</code>\n"
        f"Status: <b>{safe(order.status)}</b>\n\n"

        "👤 <b>CUSTOMER INFORMATION</b>\n"
        f"Name: {safe(order.customer_name)}\n"
        f"Phone: {safe(order.phone)}\n"
        f"Address: {safe(order.address)}\n\n"

        "💳 <b>PAYMENT METHOD</b>\n"
        f"{safe(payment_name)}\n\n"

        "🛒 <b>ORDER ITEMS</b>\n"
        f"{products_text}\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>PAYMENT SUMMARY</b>\n"
        f"Subtotal: ${float(subtotal):.2f}\n"
        f"Shipping: ${float(shipping):.2f}\n"
        f"Tax: ${float(tax):.2f}\n"
        f"Total: <b>${float(order.total):.2f}</b>\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "Thank you for choosing VELORA ❤️"
    )

    telegram_url = (
        f"https://api.telegram.org/bot{token}/sendMessage"
    )

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            telegram_url,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        if result.get("ok"):
            print("Telegram order notification sent successfully.")
            return True

        print("Telegram API error:", result)
        return False

    except Exception as error:
        print("Telegram notification failed:", error)
        return False


# ==========================================
# CHECKOUT PAGE - GET
# URL: /checkout
# ==========================================

@front_bp.route("/checkout", methods=["GET"])
@limiter.limit("30 per minute")
def checkout():

    if "user" not in session:
        flash("Please login before checkout.", "warning")
        return redirect(url_for("front.login"))

    # Get cart items
    items = get_cart()

    if not items:
        flash(
            "Your cart is empty. Please add products first.",
            "warning"
        )
        return redirect(url_for("front.cart"))

    # Calculate totals
    subtotal, shipping, tax, total = totals(items)

    # Generate order reference
    order_ref = session.get("checkout_order_ref")

    if not order_ref:
        order_ref = "VEL-" + uuid4().hex[:10].upper()
        session["checkout_order_ref"] = order_ref

    # Generate demo QR code
    qr_payload = (
        f"VELORA ORDER:{order_ref}; AMOUNT:{total:.2f} USD"
    )

    qr_url = (
        "https://api.qrserver.com/v1/create-qr-code/"
        "?size=220x220&data="
        + urllib.parse.quote(qr_payload)
    )

    return render_template(
        "front/front/checkout.html",
        cart_products=items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        total=total,
        order_ref=order_ref,
        qr_url=qr_url,
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

    # Get cart items
    items = get_cart()

    if not items:
        flash(
            "Your cart is empty or products are unavailable.",
            "warning"
        )
        return redirect(url_for("front.cart"))


    # Customer information
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    payment_method = (
        request.form.get("payment_method", "cod")
        .strip()
        .lower()
    )

    # Validate customer information
    if not all([name, phone, address]):
        flash(
            "Please complete your name, phone number, and address.",
            "danger"
        )
        return redirect(url_for("front.checkout"))

    if payment_method not in ["cod", "khqr"]:
        flash("Invalid payment method.", "danger")
        return redirect(url_for("front.checkout"))

    # Recalculate totals using server-side data
    subtotal, shipping, tax, total = totals(items)

    order_ref = session.get("checkout_order_ref")

    if not order_ref:
        order_ref = "VEL-" + uuid4().hex[:10].upper()

    # Create order
    order = Order(
        order_ref=order_ref,
        user_id=session["user"]["id"],
        customer_name=name,
        phone=phone,
        address=address,
        total=total,
        status="Pending Payment"
    )

    # Store product details for Telegram
    telegram_items = []

    try:
        db.session.add(order)

        # Save order items and update stock
        for item in items:

            product = db.session.get(
                Product,
                int(item["id"])
            )

            quantity = int(item["quantity"])

            if not product:
                raise ValueError(
                    "A product in your cart no longer exists."
                )

            if quantity < 1 or product.stock is None:
                raise ValueError(
                    f"Invalid quantity for {product.name}."
                )

            if product.stock < quantity:
                raise ValueError(
                    f"Insufficient stock for {product.name}. "
                    f"Only {product.stock} unit(s) available."
                )

            product_price = float(product.price)

            # Save order item
            order_item = OrderItem(
                order=order,
                product_id=product.id,
                title=product.name,
                price=product_price,
                quantity=quantity
            )

            db.session.add(order_item)

            # Save product details for Telegram
            telegram_items.append({
                "title": product.name,
                "price": product_price,
                "quantity": quantity
            })

            # Reduce stock
            product.stock -= quantity

        # Save order, items, and stock changes
        db.session.commit()

    except Exception as error:
        db.session.rollback()

        print("Order creation error:", error)

        flash(
            "Could not create your order. Please check your cart and product stock.",
            "danger"
        )

        return redirect(url_for("front.checkout"))

    # ==========================================
    # SEND TELEGRAM AFTER DATABASE COMMIT
    # ==========================================

    send_telegram_order(
        order=order,
        order_items=telegram_items,
        payment_method=payment_method,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax
    )

    # ==========================================
    # CLEAR CART AFTER SUCCESSFUL ORDER
    # ==========================================

    session["cart"] = {}
    session.pop("checkout_order_ref", None)
    session["last_order_id"] = order.id
    session.modified = True

    return redirect(
        url_for("front.order_success", order_id=order.id)
    )


# ==========================================
# ORDER SUCCESS PAGE
# URL: /order/success/<order_id>
# ==========================================

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
