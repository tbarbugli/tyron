from flask import Blueprint

health_check = Blueprint('health_check', __name__)

@health_check.route('/health/')
def health():
    return 'OK'
