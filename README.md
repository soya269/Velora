# VELORA Shop — Updated Project

## Main features
- SQLAlchemy/SQLite database for users, brands, categories, products, product images, orders and order items.
- Admin CRUD for users, categories, brands and products.
- Product storefront reads products directly from the database.
- Product filtering by keyword, category, brand, price range and in-stock status.
- Cart quantities are checked against current database stock.
- Checkout saves an order and its order items, reduces stock, and sends the existing Telegram notification when configured.
- Core JSON API endpoints for products, categories and brands.
- Admin dashboard counts are calculated from database records.

## Run on Windows PowerShell

```powershell
cd path\to\VELORA_SHOP
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open:
- Storefront: http://127.0.0.1:8000/
- Product catalog: http://127.0.0.1:8000/products
- Cart: http://127.0.0.1:8000/cart
- Admin login: http://127.0.0.1:8000/admin/login
- Admin dashboard: http://127.0.0.1:8000/admin/dashboard
- Core products API: http://127.0.0.1:8000/api/core/products
- Core categories API: http://127.0.0.1:8000/api/core/categories
- Core brands API: http://127.0.0.1:8000/api/core/brands

The app creates a default admin only when the database does not already contain username `admin`:
- Username: `admin`
- Password: `admin123`

If your uploaded database already has an admin account, continue using its existing password.

## Existing database upgrade
The project includes a small, safe SQLite startup upgrade. It creates the `brands` table and adds `products.brand_id`, `products.rating`, `orders.order_ref`, and `users.updated_at` when missing. Existing products, users and orders are preserved. Make a backup of `instance/velora.db` before running the updated project.

## Dynamic QR payment note
The checkout page now displays a unique order reference and a QR image containing that reference and the amount. This is a demonstration QR, **not a bank-issued KHQR/Bakong payment request** and it does not verify that a payment was received. To accept real QR payments, connect a merchant KHQR/Bakong payment provider and verify its payment callback/status before marking an order as paid.

## Security notes
- CSRF protection remains enabled for browser forms.
- Explicit rate limits are applied to selected Admin/Front write/login endpoints. There is no global rate limit on Core API, so it can be tested independently.
- Use a strong `SECRET_KEY` and real production database credentials before deployment.

## Telegram configuration
Copy `.env.example` to `.env`, then enter your own Telegram bot token and chat ID if you want order notifications. The delivered `.env` intentionally has blank Telegram credentials; the token from the uploaded archive was not copied into the updated archive. Do not commit `.env` to Git.
