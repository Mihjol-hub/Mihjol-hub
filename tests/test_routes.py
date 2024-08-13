#app/test_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from . import db
from .models import User, Group, GroupMember, Keyword, Friendship, Notification, Post, Reaction, Comment
from validate_email import validate_email

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Welcome to Linkedin CUI"

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not validate_email(data['email']):
        return jsonify({"message": "Invalid email address"}), 400
    if 'confirm_password' not in data or data['password'] != data['confirm_password']:
        return jsonify({"message": "Passwords do not match"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=user.id)
    return jsonify({'message': 'User registered successfully', 'access_token': access_token}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@main.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"msg": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response, 200

@main.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({'username': user.username, 'email': user.email}), 200


