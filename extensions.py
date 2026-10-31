from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
# No global default: API endpoints remain independently testable.
# Add explicit @limiter.limit(...) to Admin and Front endpoints.
limiter = Limiter(key_func=get_remote_address, default_limits=[])
