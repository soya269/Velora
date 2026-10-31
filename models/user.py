from extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    profile = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False, default="Staff")
    status = db.Column(db.String(20), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def to_dict(self, include_email=True):
        data = {"id": self.id, "name": self.name, "username": self.username,
                "role": self.role, "status": self.status}
        if include_email: data["email"] = self.email
        return data
