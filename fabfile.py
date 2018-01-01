import os
from sys import platform
from contextlib import contextmanager

from fabric.api import local
from fabric.context_managers import prefix
from fabric.operations import sudo
from fabric.state import env


# with settings(warn_only=True):
#     result = local('./manage.py test my_app', capture=True)
# if result.failed and not confirm("Tests failed. Continue anyway?"):
#     abort("Aborting at user request.")
# run("python manage.py makemigrations --settings=project.settings.development")

# env.hosts =['127.0.0.1']
env.hosts = ['localhost']
env.src_folder = os.path.dirname(os.path.realpath(__file__))
env.project_folder = os.path.dirname(env.src_folder)
env.is_linux = 'linux' in platform
env.activate = '/bin/bash -l -c "source ../venv/bin/activate"' if env.is_linux else '..\\venv\\Scripts\\activate.bat'
env.venv_folder = os.path.join(env.project_folder, 'venv')


def init():
    def create_venv():
        # result = local(env.activate)
        # print(result)
        # return

        if not os.path.exists(env.venv_folder):
            python_interpreter = ' -p python3' if env.is_linux else ''
            local('virtualenv ../venv' + python_interpreter)
            # local('virtualenv ../venv' + python_interpreter, shell='/bin/bash -l -c')
            with virtualenv():
                local('pip install gunicorn')
            requirements()
        else:
            print('venv existed', env.venv_folder)

    def create_folders_and_files():
        BACKUP_ROOT = os.path.join(env.project_folder, 'backup')
        LOGS_ROOT = os.path.join(env.project_folder, 'logs', 'logs.txt')
        if not os.path.exists(BACKUP_ROOT):
            os.mkdir(BACKUP_ROOT)
        if not os.path.exists(os.path.dirname(LOGS_ROOT)):
            os.mkdir(os.path.dirname(LOGS_ROOT))
            open(LOGS_ROOT, 'a').close()

    create_venv()
    create_folders_and_files()


@contextmanager
def virtualenv():
    with prefix(env.activate):
        command = 'where' if not env.is_linux else 'which'
        local(command + ' python')
        yield


def cs():
    with virtualenv():
        # needs to be confirmed
        local('python manage.py collectstatic --noinput')


def pull():
    local('git pull')


def makemigrations():
    with virtualenv():
        local('python manage.py makemigrations')


def migrate():
    with virtualenv():
        local('python manage.py migrate')


def db():
    makemigrations()
    migrate()


def celery():
    with virtualenv():
        local('celery -A mysite worker -l info')


def celery_win():
    with virtualenv():
        local('celery -A mysite worker --pool=solo -l info')


def requirements():
    with virtualenv():
        local('sudo pip install -r requirements.txt')


def shell():
    with virtualenv():
        local('python manage.py shell')


def freeze():
    with virtualenv():
        local('pip freeze')


def venv(command):
    """fab venv:"pip freeze" -- to execute any command in enviroment"""
    with virtualenv():
        local(command)


def manage(command):
    with virtualenv():
        local('python manage.py ' + command)


def runserver():
    with virtualenv():
        local('python manage.py runserver')


def deploy():
    pull()
    cs()
    # requirements()
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
