
import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD .ENV
# ============================================================

load_dotenv(BASE_DIR / ".env")


# ============================================================
# DATABASE
# ============================================================

DATABASE_FILE = INSTANCE_DIR / "velora.db"

DEFAULT_DATABASE_URL = (
    "sqlite:///"
    + DATABASE_FILE.as_posix()
)


# ============================================================
# FLASK CONFIGURATION
# ============================================================

class Config:

    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    SECRET_KEY = os.environ.get("SECRET_KEY")

    # A development-only fallback keeps local setup convenient.
    # Production must provide a long, random SECRET_KEY in its .env.
    if not SECRET_KEY:
        if os.environ.get("FLASK_ENV", "").lower() == "production":
            raise RuntimeError("SECRET_KEY must be set in production.")
        SECRET_KEY = "dev-only-change-this-secret-before-deployment"


    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    SQLALCHEMY_DATABASE_URI = DEFAULT_DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # --------------------------------------------------------
    # Upload folders
    # --------------------------------------------------------

    UPLOAD_FOLDER = str(
        BASE_DIR / "static" / "uploads"
    )

    USER_UPLOAD_FOLDER = str(
        BASE_DIR / "static" / "uploads" / "users"
    )

    CATEGORY_UPLOAD_FOLDER = str(
        BASE_DIR / "static" / "uploads" / "categories"
    )

    PRODUCT_UPLOAD_FOLDER = str(
        BASE_DIR / "static" / "uploads" / "products"
    )


    # --------------------------------------------------------
    # Maximum upload size
    # --------------------------------------------------------
    # 32 MB total request size.
    #
    # This allows:
    # - 1 thumbnail
    # - multiple product images
    # - normal form data
    #
    # If you need larger files later, increase this value.
    # --------------------------------------------------------

    MAX_CONTENT_LENGTH = 32 * 1024 * 1024


    # --------------------------------------------------------
    # Order settings
    # --------------------------------------------------------

    SHIPPING_COST = float(
        os.environ.get(
            "SHIPPING_COST",
            "15"
        )
    )

    TAX_RATE = float(
        os.environ.get(
            "TAX_RATE",
            "0.05"
        )
    )


    # --------------------------------------------------------
    # Telegram
    # --------------------------------------------------------

    TELEGRAM_BOT_TOKEN = os.environ.get(
        "TELEGRAM_BOT_TOKEN"
    )

    TELEGRAM_CHAT_ID = os.environ.get(
        "TELEGRAM_CHAT_ID"
    )

    TELEGRAM_TIMEOUT = int(
        os.environ.get(
            "TELEGRAM_TIMEOUT",
            "15"
        )
    )


    # --------------------------------------------------------
    # Flask port
    # --------------------------------------------------------

    PORT = int(
        os.environ.get(
            "PORT",
            "8000"
        )
    )


