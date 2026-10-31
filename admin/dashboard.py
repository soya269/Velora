from flask import render_template
from . import admin_bp
from .auth import admin_required
from models import User, Order, Product, Category, Brand

@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():
    return render_template(
        "front/admin/dashboard/index.html",
        total_products=Product.query.count(),
        total_categories=Category.query.count(),
        total_brands=Brand.query.count(),
        total_users=User.query.count(),
        total_orders=Order.query.count(),
        recent_orders=Order.query.order_by(Order.id.desc()).limit(8).all()
    )
