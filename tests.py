from functools import partial
import gevent
import json
import mock
import redis
from redis.client import PubSub
from mock import MagicMock
from mock import patch
import unittest
from tyron.tyron import subscriptions
from tyron.tyron import RedisSub
from tyron.tyron import subscriptions

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
