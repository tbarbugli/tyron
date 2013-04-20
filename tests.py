from functools import partial
import gevent
import json
from redis.client import PubSub
from mock import patch
from tyron.tyron import application
from tyron.tyron import subscriptions
from tyron.tyron import RedisSub

try:
    import unittest2 as unittest
except ImportError:
    import unittest

redis_pubsub = RedisSub('channel', 'localhost', 6379, 1)
pubsub_channel = []

def pubsub_stream(*args):
    return (m for m in pubsub_channel)

class TestRedisPubSub(unittest.TestCase):

    def tearDown(self):
        pubsub_channel[:] = []

    @patch.object(PubSub, 'listen', pubsub_stream)
    @patch.object(PubSub, 'execute_command')
    def test_subscribes_to_redis(self, pubsub_exec, *args):
        redis_pubsub.subscribe()
        pubsub_exec.assert_called_with('SUBSCRIBE', 'channel')

    def test_redis_connection_from_init(self):
        redis_pubsub = RedisSub('channel', 'redis.local', 6380, 1, 'xxx')
        client = redis_pubsub.get_redis_connection()
        configs = client.connection_pool.connection_kwargs
        assert configs['host'] == 'redis.local'
        assert configs['port'] == 6380
        assert configs['db'] == 1
        assert configs['password'] == 'xxx'

    def test_message_parsing(self):
        message = {
            'channel': 'channelname',
            'data': 'data'
        }
        encoded_message = json.dumps(message)
        r_message = redis_pubsub.parse_message(encoded_message)
        assert 'channelname', 'data' == r_message

    @patch.object(PubSub, 'listen', pubsub_stream)
    @patch.object(PubSub, 'execute_command')
    def test_message_faulty_parsing_handling(self, pubsub_exec, *args):

        def subscriber(channel):
            return subscriptions[channel].get(timeout=3)

        getter = gevent.spawn(partial(subscriber, 'answer_to_everything'))

        bad_payload = {
            'type': 'message',
            'data': '{s"this is not json loadable}',
        }
        bad_format = {
            'type': 'message',
            'data': '{"data": "41"}',
        }
        good_payload = {
            'type': 'message',
            'data': '{"data": "42", "channel": "answer_to_everything"}',
        }
        pubsub_channel[:] = [bad_payload, good_payload, bad_format]
        setter = gevent.spawn(redis_pubsub.subscribe)
        gevent.joinall([getter, setter])
        assert getter.value == "42"

class TestHealthPlugin(unittest.TestCase):

    def test_registered_ext_health(self):
        self.assertIn('health_check', application.blueprints)

    def test_url_ext_health(self):
        client = application.test_client()
        response = client.get('/health/')
        self.assertEqual(response.status_code, 200)
