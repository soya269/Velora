from pathlib import Path
import sqlite3
from flask import Flask, session, render_template
from config import Config, DATABASE_FILE
from extensions import db, migrate, csrf, limiter
from dotenv import load_dotenv


app = Flask(__name__)
app.config.from_object(Config)

for folder in (app.config["UPLOAD_FOLDER"], app.config["USER_UPLOAD_FOLDER"],
               app.config["CATEGORY_UPLOAD_FOLDER"], app.config["PRODUCT_UPLOAD_FOLDER"]):
    Path(folder).mkdir(parents=True, exist_ok=True)
load_dotenv()
db.init_app(app)
migrate.init_app(app, db)
csrf.init_app(app)
limiter.init_app(app)

from models import User, Order, OrderItem, Category, Brand, Product, ProductImage
from front import front_bp
from admin import admin_bp
from api import api_bp
from api.core import core_bp

app.register_blueprint(core_bp)
app.register_blueprint(front_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)
csrf.exempt(api_bp)
csrf.exempt(core_bp)

@app.context_processor
def inject_globals():
    cart = session.get("cart", {})

    cart_count = 0

    if isinstance(cart, dict):
        # Cart format: {"1": 2, "3": 1}
        for quantity in cart.values():
            try:
                cart_count += int(quantity)
            except (TypeError, ValueError):
                continue

    elif isinstance(cart, list):
        # Support the alternative list-based cart format
        for item in cart:
            if isinstance(item, dict):
                try:
                    cart_count += int(item.get("quantity", item.get("qty", 1)))
                except (TypeError, ValueError):
                    continue

    return {"cart_count": cart_count}
@app.errorhandler(404)
def not_found(error):
    try:
        return render_template("front/front/404.html"), 404
    except Exception:
        return "Page not found", 404

def init_db():
    with app.app_context():
        db.create_all()
        # Safe SQLite upgrades for existing VELORA databases (preserves current data).
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            conn = sqlite3.connect(str(DATABASE_FILE))
            try:
                product_cols = [r[1] for r in conn.execute("PRAGMA table_info(products)")]
                if "brand_id" not in product_cols:
                    conn.execute("ALTER TABLE products ADD COLUMN brand_id INTEGER REFERENCES brands(id)")
                if "rating" not in product_cols:
                    conn.execute("ALTER TABLE products ADD COLUMN rating NUMERIC(3,2) NOT NULL DEFAULT 0")
                order_cols = [r[1] for r in conn.execute("PRAGMA table_info(orders)")]
                if "order_ref" not in order_cols:
                    conn.execute("ALTER TABLE orders ADD COLUMN order_ref VARCHAR(40)")
                user_cols = [r[1] for r in conn.execute("PRAGMA table_info(users)")]
                if "updated_at" not in user_cols:
                    conn.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME")
                conn.commit()
            finally:
                conn.close()
        # Never create a predictable default administrator account here.
        # Existing users (including the current administrator) remain untouched.
        for name in ["Fashion", "Electronics", "Furniture", "Shoes", "Miscellaneous"]:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name, description=f"{name} products"))
        db.session.commit()

# Database initialization is not run automatically during Gunicorn startup.

if __name__ == "__main__":
    app.run(debug=True, port=app.config.get("PORT", 8000))
