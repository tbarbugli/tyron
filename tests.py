import json
import mock
import redis
from redis.client import PubSub
from mock import MagicMock
from mock import patch
import unittest
from tyron.tyron import subscriptions
from tyron.tyron import RedisSub

redis_pubsub = RedisSub('channel', 'localhost', 6379, 1)

class TestRedisPubSub(unittest.TestCase):

    @patch.object(PubSub, 'listen')
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

    def test_redis_config(self):
        pass

    def test_timeout(self):
        pass
