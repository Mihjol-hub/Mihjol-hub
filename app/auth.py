#app/auth.py
#app/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_jwt_extended import get_jwt, jwt_required, create_access_token, unset_jwt_cookies, get_jwt_identity
from app.models import TokenBlocklist
from app import db, jwt
from datetime import datetime, timezone

auth = Blueprint('auth', __name__)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

# Keep the logout route here if you want to use it for API logout
@auth.route('/api/logout', methods=['POST'])
@jwt_required()
def api_logout():
    jti = get_jwt()['jti']
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify({'message': 'JWT revoked'}), 200