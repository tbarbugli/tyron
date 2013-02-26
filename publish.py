from fabric.api import local, run, env, roles
import tyron

def test():
    local('python setup.py sdist')

def publish(release):
    test()
    local('rm -rf dist/')
    local('python setup.py sdist upload')
