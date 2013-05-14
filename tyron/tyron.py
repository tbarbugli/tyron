from collections import defaultdict
import json
from flask import Flask
import gevent
from gevent.event import AsyncResult
from gevent.timeout import Timeout
from gevent import monkey
import os
import logging
import redis
from .utils import crossdomain
from .utils import load_plugin


monkey.patch_all()

application = Flask(__name__)
application.config.from_object('tyron.default_settings')

if 'TYRON_CONF' in os.environ:
    application.config.from_envvar('TYRON_CONF')

application.logger.setLevel(application.config['LOG_LEVEL'])
logger = logging.getLogger(__name__)

for plugin_path in application.config['EXTENSIONS']:
    logger.info('registering extension %s ...' % plugin_path)
    plugin = load_plugin(plugin_path)
    application.register_blueprint(plugin)

subscriptions = defaultdict(AsyncResult)

class RedisSub(gevent.Greenlet):
    """
    subscribes to a redis pubsub channel and routes
    messages to subscribers

    messages have this format
    {'channel': ..., 'data': ...}

    """

    def __init__(self, pubsub_channel, redis_hostname, redis_port, redis_db, redis_password=None):
        gevent.Greenlet.__init__(self)
        self.pubsub_channel = pubsub_channel
        self.redis_hostname = redis_hostname
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password

    def get_redis_connection(self):
        return redis.Redis(self.redis_hostname, self.redis_port, self.redis_db, self.redis_password)

    def decode_message(self, message):
        return json.loads(message)

    def parse_message(self, message):
        msg = self.decode_message(message)
        return msg['channel'], msg['data']

    def handle_message(self, message):
        try:
            channel, data = self.parse_message(message)
        except:
            logger.exception('unable to parse the message %r' % message)
        else:
            async_result = subscriptions[channel]
            async_result.set(data)
            del subscriptions[channel]

    def subscribe(self):
        connection = self.get_redis_connection()
        pubsub = connection.pubsub()
        pubsub.subscribe(self.pubsub_channel)
        for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            self.handle_message(message['data'])

    def _run(self):
        self.subscribe()

@application.route('/favicon.ico/')
def favicon():
    return ''

@application.route('/<channel>/', methods=('GET', 'POST', 'OPTIONS'))
@crossdomain(origin='*')
def subscribe(channel):
    timeout = application.config['LONGPOLLING_TIMEOUT']
    try:
        message = subscriptions[channel].get(timeout=timeout)
    except Timeout:
        message = application.config['TIMEOUT_RESPONSE_MESSAGE']
    return message

@application.before_first_request
def start_subscribe_loop():
    pubsub = RedisSub(
        pubsub_channel=application.config['CHANNEL_NAME'],
        redis_hostname=application.config['REDIS_HOSTNAME'],
        redis_port=application.config['REDIS_PORT'],
        redis_db=application.config['REDIS_DB']
    )
    gevent.spawn(pubsub.start)

def main():
    from gevent.wsgi import WSGIServer
    WSGIServer(('', 8080), application).serve_forever()

if __name__ == '__main__':
    main()
