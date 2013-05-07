from flask import Blueprint
import redis
from tyron.utils import crossdomain


redis_store = Blueprint('redis_store', __name__)

@redis_store.route('/store/<key>/', methods=('GET', 'POST'))
@crossdomain(origin='*')
def store(key):
    from tyron.tyron import application
    client = redis.Redis(
        application.config['REDIS_HOSTNAME'],
        application.config['REDIS_PORT'],
        application.config['REDIS_DB']
    )
    value = client.get(key)
    if value is None:
        return application.config['TIMEOUT_RESPONSE_MESSAGE']
    return value