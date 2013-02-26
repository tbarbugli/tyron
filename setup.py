from setuptools import find_packages
from setuptools import setup

import tyron

description="""
Gevent redis/pubsub event notifier written in flask and gevent
"""

setup(
    name="tyron",
    version=tyron.__version__,
    url='https://github.com/tbarbugli/tyron',
    license='BSD',
    platforms=['OS Independent'],
    description = description.strip(),
    author = 'Tommaso Barbugli',
    author_email = 'tbarbugli@gmail.com',
    maintainer = 'Tommaso Barbugli',
    maintainer_email = 'tbarbugli@gmail.com',
    packages=find_packages(),
    tests_require=[
        'mock',
    ],
    test_suite='tests',
    dependency_links = [
        'https://github.com/downloads/SiteSupport/gevent/gevent-1.0rc2.tar.gz#egg=gevent'
    ],
    requires = [
        'Flask (==0.9)',
        'Jinja2 (==2.6)',
        'Werkzeug (==0.8.3)',
        'greenlet (==0.4.0)',
        'gunicorn (==0.17.2)',
        'redis (==2.7.2)',
        'ujson (==1.30)',
    ],
    entry_points={
        'console_scripts': [
            'tyron = tyron:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ]
)