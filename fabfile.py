import os
from sys import platform
from contextlib import contextmanager

from fabric.api import local
from fabric.context_managers import prefix
from fabric.state import env


# fab hello:name=Jeff
# fab hello:Jeff
# with settings(warn_only=True):
#     result = local('./manage.py test my_app', capture=True)
# if result.failed and not confirm("Tests failed. Continue anyway?"):
#     abort("Aborting at user request.")


# run("python manage.py makemigrations --settings=project.settings.development")


env.src_folder = os.path.dirname(os.path.realpath(__file__))
env.project_folder = os.path.dirname(env.src_folder)
env.is_linux = platform == 'linux'
env.activate = 'source ../venv/bin/activate' if env.is_linux else '..\\venv\\Scripts\\activate.bat'


def init():
    # TODO: create backup, logs -- import from settings
    def create_venv():
        if not os.path.exists(os.path.join(env.project_folder, 'venv')):
            # TODO: virtualenv -p /usr/bin/python3.4 venv
            local('virtualenv ../venv')
            requirements()
        else:
            print('venv existed')

    create_venv()


@contextmanager
def virtualenv():
    with prefix(env.activate):
        local('where python')
        yield


def cs():
    with virtualenv():
        local('python manage.py collectstatic')
        # needs to be confirmed


def pull():
    local('git pull')


def makemigrations():
    with virtualenv():
        local('python manage.py makemigrations')


def migrate():
    with virtualenv():
        local('python manage.py migrate')


def requirements():
    with virtualenv():
        local('pip install -r requirements.txt')


def deploy():
    pull()
    cs()
    requirements()
    migrate()
    # restart nginx


# def backup():
#     with virtualenv():
#         pass


def restart():
    # user=movie, db_name=movie, supervisor=movie --
    # this will make it easier because I can get user's name I am logged as
    pass
    # gunicorn
    # nginx
    # supervisor
