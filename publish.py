from fabric.api import local, run, env, roles
import tyron

def test():
    local('python setup.py sdist')

def publish(release):
    test()
    local('git flow feature finish %s' % release)
    local('git flow release start v%s' % tyron.__version__)
    local('rm -rf dist/')
    local('setup.py sdist upload')
    local('git push origin :release/%s' % release)
    local('git branch -d release/%s' % release)
