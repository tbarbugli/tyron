from fabric.api import local, run, env, roles
import tyron

def test():
    local('python setup.py sdist')
    # local('python setup.py test')

def publish():
    test()
    local('rm -rf dist/')
    local('python setup.py sdist upload')
    local('git tag v%s' % tyron.__version__)
    local('git push --tags')
