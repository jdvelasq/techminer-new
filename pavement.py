"""paver config file"""

# from testing python book
from paver.easy import sh
from paver.tasks import task, needs


@task
def tests():
    """unit testing"""
    # sh('nosetests --verbose --cover-package=techminer --cover-tests '
    #   ' --with-doctest --rednose  ./techminer/')
    sh("pytest --doctest-modules")


@task
def pylint():
    """pyltin"""
    sh("pylint ./techminer/")


@task
def pypi():
    """Instalation on PyPi"""
    sh("python setup.py sdist")
    sh("twine upload dist/*")


@task
def local():
    """local install"""
    sh("pip3 uninstall --yes techminer")
    sh("python3 setup.py install develop")


@task
def sphinx():
    """Document creation using Shinx"""
    sh("cd sphinx; make html; cd ..")
    sh("rm -rf docs/*")
    sh("mv  sphinx/_build/html/* docs/")
    sh("rm -R sphinx/_build/doctrees/*")


@needs("nosetests", "pylint", "sphinx")
@task
def default():
    """default"""
    pass
