# from flask import render_template, request, redirect, url_for, flash
# from extensions import db
# from models import Order
# from . import admin_bp
# from .auth import admin_required
#
# @admin_bp.route("/orders")
# @admin_required
# def admin_orders():
#     orders=Order.query.order_by(Order.id.desc()).all()
#     return render_template("front/admin/orders/index.html",orders=orders)
#
# @admin_bp.route("/orders/<int:id>/status",methods=["POST"])
# @admin_required
# def update_order_status(id):
#     order=Order.query.get_or_404(id)
#     status=request.form.get("status","Pending")
#     if status not in {"Pending","Processing","Shipped","Completed","Cancelled"}: status="Pending"
#     order.status=status; db.session.commit()
#     flash("Order status updated.","success")
#     return redirect(url_for("admin.admin_orders"))

from flask import render_template, request, redirect, url_for, flash

from extensions import db
from models import Order
from . import admin_bp
from .auth import admin_required


# ==========================================
# ADMIN ORDER MANAGEMENT
# URL: /admin/orders
# ==========================================

@admin_bp.route("/orders", methods=["GET"])
@admin_required
def admin_orders():

    orders = Order.query.order_by(Order.id.desc()).all()

    return render_template(
          "front/admin/orders/index.html",
        orders=orders
    )


# ==========================================
# UPDATE ORDER STATUS
# URL: /admin/orders/<id>/status
# ==========================================

@admin_bp.route("/orders/<int:id>/status", methods=["POST"])
@admin_required
def update_order_status(id):

    order = db.session.get(Order, id)

    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("admin.admin_orders"))

    allowed_statuses = {
        "Pending Payment",
        "Pending",
        "Processing",
        "Shipped",
        "Completed",
        "Cancelled"
    }

    status = request.form.get("status", "Pending")

    if status not in allowed_statuses:
        flash("Invalid order status.", "danger")
        return redirect(url_for("admin.admin_orders"))

    order.status = status

    try:
        db.session.commit()
        flash("Order status updated successfully.", "success")

    except Exception as error:
        db.session.rollback()
        print("Update order status error:", error)
        flash("Could not update order status.", "danger")

    return redirect(url_for("admin.admin_orders"))
