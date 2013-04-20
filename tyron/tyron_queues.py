from collections import defaultdict

try:
    import ujson as json
except ImportError:
    import json

from flask import Flask
import gevent
from gevent import queue
import os
import logging
import redis


application = Flask(__name__)
application.config.from_object('tyron.default_settings')
if 'TYRON_CONF' in os.environ:
    application.config.from_envvar('TYRON_CONF')
application.logger.setLevel(application.config['LOG_LEVEL'])

# class SubscriptionList(object):

#     def __init__(self):
#         self.subscriptions = defaultdict(set)

#     def add(self, client, channel):
#         self.subscriptions[channel].add(client)

#     def remove(self, client, channel):
#         """
#         removes the client from subscriptions

#         """
#         if client in self.subscriptions[channel]:
#             self.subscriptions[channel].remove(client)
#         if len(self.subscriptions[channel]) == 0:
#             del self.subscriptions['channel']

#     def emit(self, channel, data):
#         for subscription in self.subscriptions[channel]:
#             subscription.queue.put_nowait(data)

# class Client(object):
#     def __init__(self):
#         self.queue = queue.Queue()

# subscriptions = SubscriptionList()

subscriptions = defaultdict(queue.Queue)

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

    def parse_message(self, message):
        msg = json.loads(message)
        return msg['channel'], msg['data']

    def handle_message(self, message):
        channel, data = self.parse_message(message)
        subscriptions.emit(channel, data)

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

@application.route('/')
def health():
    return 'OK'

@application.route('/<channel>/')
def subscribe(channel):
    # client = Client()
    # subscriptions.add(client, channel)
    timeout = application.config['LONGPOLLING_TIMEOUT']
    try:
        # message = client.queue.get(timeout=timeout)
        message = subscriptions[channel].get(timeout=timeout)
    except queue.Empty:
        message = application.config['TIMEOUT_RESPONSE_MESSAGE']
    # finally:
        # subscriptions.remove(client, channel)
    return message

def start_subscribe_loop():
    pubsub = RedisSub(
        pubsub_channel=application.config['CHANNEL_NAME'],
        redis_hostname=application.config['REDIS_HOSTNAME'],
        redis_port=application.config['REDIS_PORT'],
        redis_db=application.config['REDIS_DB']
    )
    gevent.spawn(pubsub.start)

def main():
    start_subscribe_loop()
    application.run()

if __name__ == '__main__':
    main()
