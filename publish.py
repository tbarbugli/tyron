from fabric.api import local, run, env, roles
import tyron

def test():
    local('python setup.py sdist')

def release():
    version = tyron.__version__
    test()
    local('git flow release finish %s' % version)
    local('git checkout %s' % version)
    local('rm -rf dist/')
    local('setup.py sdist upload')
    local('git push origin :release/%s' % version)
    local('git branch -d release/%s' % version)