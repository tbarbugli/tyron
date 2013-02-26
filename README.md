Tyron
======
Tyron is a web app to send push events to connected clients

A client connects to tyron and subscribes to a specific channel,
tyron will keep the http connection open until something get published
to that channel.

To keep the connection count as little as possible open connection will
timeout after a configurable interval of time.

The messaging backend utilises the redis pub/sub feature.

Subscribe to channels
====================
Clients subscribes to channel using the /<channel>/ entry point

Publish to clients
==================
To publish to a client you need to connect to redis and publish
on the channel tyron subscribes (see CHANNEL_NAME setting)

NOTE: The user channel is part of the message you publish to redis

Message format
==============
Messages must follow this json format:

`{"channel": "user_channel", "data": "...."}`


Example:
========

client side: POST to /hiphop/
tyron subscribes the client to hiphop channel

`{"channel": "hiphop", "data": "...."}`


Install
=======

Just do pip install tyron or do a setup.py install

Note: If you are using OSX you might need something like this:

`CFLAGS="-I /opt/local/include -L /opt/local/lib" pip install tyron`

Settings
======== 

**DEBUG**

Run Flask in debug mode

**LONGPOLLING_TIMEOUT**

`Default: 3`

The timeout in seconds for connections waiting for 

**TIMEOUT\_RESPONSE_MESSAGE**

`Default: str('')`

The message the webserver will return to clients when LONGPOLLING_TIMEOUT occours

**CHANNEL_NAME**

`Default: tyron_pubsub`

The redis pub/sub channel tyron subscribes to

**REDIS_HOSTNAME**

`Default: localhost`


**REDIS_PORT**

`Default: 6379`


**REDIS_DB**

`Default: 0`


**LOG_LEVEL**

`Default: logging.INFO`

The loglevel (from python logging module)

You can override settings pointing tyron to your own settings module.
The settings module must be specified in the TYRON_CONF environment variable.

eg.

`TYRON_CONF=my_settings.py python tyron.py`


DEPLOY
======

tyron is a WSGI app so you have lots of choice in terms of web servers :)
You definetely wants to opt for some async worker as tyron will keep an high amount of open idle connections (so gevent/libevent ...)

I personally like the semplicity of green unicorn:


`
pip install gunicorn
gunicorn -b :8091 -w 9 -k gevent --worker-connections=2000 tyron --log-level=critical
`   

few notes about chosen parameters:

-k gevent tells gunicorn to use the gevent worker
-w 9 means, spawn 9 worker processes (2-4 * cpu_cores is suggested)
--worker-connections 2000 every worker process will handle 2000 connections


DEPLOY CAVEATS
==============

On high traffic web sites is quite easy to hit some common limit of your kernel
limits, the first limit you are probably going to hit is the file descriptor limit.
By default Ubuntu (and many other OS) have the very low file descriptor limit of 1024
I suggest to benchmark your machine running tyron to find the best value for this limit and update it.

Verbose logging can lead to issues, unless the logging facility you are using handles that for you.
Logging INFO/DEBUG messages can easily lead to high cpu usage.


BENCHMARKS
==========

coming soon ...

.using an EC2 medium instance and bees with machine guns




