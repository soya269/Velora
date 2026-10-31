from flask import jsonify, request
from werkzeug.security import generate_password_hash
from extensions import db, limiter
from models import User
from . import api_bp

def user_data(u):
    return u.to_dict()

@api_bp.route("/users", methods=["GET"])
def get_users():
    return jsonify({"success":True,"users":[user_data(u) for u in User.query.order_by(User.id.desc()).all()]})

@api_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    u=User.query.get_or_404(user_id); return jsonify({"success":True,"user":user_data(u)})

@api_bp.route("/users", methods=["POST"])
@limiter.limit("60 per minute")
def create_user():
    data=request.get_json(silent=True) or {}
    if not all(data.get(k) for k in ("name","username","email","password")): return jsonify({"success":False,"message":"name, username, email and password are required"}),400
    if User.query.filter((User.username==data["username"])|(User.email==data["email"].lower())).first(): return jsonify({"success":False,"message":"Username or email already exists"}),409
    u=User(name=data["name"].strip(),username=data["username"].strip(),email=data["email"].lower().strip(),password=generate_password_hash(data["password"]),role=data.get("role","Staff"),status=data.get("status","Active"))
    db.session.add(u); db.session.commit(); return jsonify({"success":True,"user":user_data(u)}),201

@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@limiter.limit("60 per minute")
def update_user(user_id):
    u=User.query.get_or_404(user_id); data=request.get_json(silent=True) or {}
    for key in ("name","username","email","role","status"):
        if key in data: setattr(u,key,data[key])
    if data.get("password"): u.password=generate_password_hash(data["password"])
    db.session.commit(); return jsonify({"success":True,"user":user_data(u)})

@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@limiter.limit("30 per minute")
def delete_user(user_id):
    u=User.query.get_or_404(user_id); db.session.delete(u); db.session.commit(); return jsonify({"success":True,"message":"User deleted successfully"})
