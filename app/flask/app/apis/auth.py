
from flask import Blueprint, request, current_app
#import jwt

auth = Blueprint('auth', __name__)

def token_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('auth-access-token')
        if not token:
            return jsonify({'message' : 'access token missing'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET-KEY'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message' : 'Token expired !!'}), 401
        return func(*args, **kwargs)
    return wrapper



