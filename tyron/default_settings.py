import logging

DEBUG = False
TIMEOUT_RESPONSE_MESSAGE = ''
LONGPOLLING_TIMEOUT = 15
CHANNEL_NAME = 'notifications_pubsub'
REDIS_HOSTNAME = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
HTTP_PORT = 8080
LOG_LEVEL = logging.INFO
EXTENSIONS = ['tyron.ext.health.health_check']