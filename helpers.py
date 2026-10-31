from flask import request, current_app


# ==========================================
# GET CATEGORIES
# ==========================================

def get_categories():
    from models.category import Category
    return Category.query.order_by(Category.name.asc()).all()


# ==========================================
# CART ITEMS
# ==========================================

def cart_items():
    return request.cookies.get("unused", [])


# ==========================================
# CALCULATE TOTALS
# ==========================================

def calculate_totals(items):

    subtotal = 0

    for item in items:
        price = float(item.get("price", 0))
        quantity = int(
            item.get(
                "quantity",
                item.get("qty", 1)
            )
        )

        subtotal += price * quantity

    shipping_cost = current_app.config.get(
        "SHIPPING_COST",
        0
    )

    tax_rate = current_app.config.get(
        "TAX_RATE",
        0
    )

    shipping = shipping_cost if subtotal > 0 else 0
    tax = subtotal * tax_rate
    total = subtotal + shipping + tax

    return {
        "subtotal": round(subtotal, 2),
        "shipping": round(shipping, 2),
        "tax": round(tax, 2),
        "total": round(total, 2)
    }


# ==========================================
# LOAD USERS
# ==========================================

def load_users():

    from models.user import User

    return User.query.order_by(
        User.id.desc()
    ).all()


# ==========================================
# LOAD ORDERS
# ==========================================

def load_orders():

    from models.order import Order

    return Order.query.order_by(
        Order.id.desc()
    ).all()

# from flask import request, current_app
# from products import products
# import json, os
# from models.category import Category
#
#
# def get_categories():
#     result, seen = [], set()
#     for product in products:
#         category = product.get("category") or {}
#         name = category.get("name")
#         if name and name.lower() not in seen:
#             result.append(category)
#             seen.add(name.lower())
#     return result
#
# def cart_items():
#     return request.cookies.get("unused", [])  # kept for compatibility
#
# def calculate_totals(items):
#     subtotal = sum(float(i.get("price", 0)) * int(i.get("quantity", i.get("qty", 1))) for i in items)
#     shipping = current_app.config["SHIPPING_COST"] if subtotal else 0
#     tax = subtotal * current_app.config["TAX_RATE"]
#     return {"subtotal": round(subtotal,2), "shipping": round(shipping,2),
#             "tax": round(tax,2), "total": round(subtotal+shipping+tax,2)}
#
# def load_users():
#     from models.user import User
#     return User.query.order_by(User.id.desc()).all()
#
# def load_orders():
#     from models.order import Order
#     return Order.query.order_by(Order.id.desc()).all()

