from fabric.api import local
# fab hello:name=Jeff
# fab hello:Jeff
# with settings(warn_only=True):
#     result = local('./manage.py test my_app', capture=True)
# if result.failed and not confirm("Tests failed. Continue anyway?"):
#     abort("Aborting at user request.")

# code_dir = '/srv/django/myproject'
# with cd(code_dir):


# code_dir = 'backend-directory'
#
# if exists(code_dir):
#    run('cd %s && git pull' % (code_dir,))
# else:
#    run("git clone git://serveraddress/projects/backend-directory")

# with cd(code_dir):
#   sudo("pip install virtualenv")
#   run("virtualenv -p /usr/bin/python3.4 venv")
#   run("source venv/bin/activate")
#   #sudo("pip install -r requirements/dev.txt")
#   sudo("pip install -r requirements/production.txt")

# with settings(warn_only=True):
#     with settings(sudo_user='postgres'):
#         sudo("psql -c " + '"CREATE USER new_user WITH PASSWORD ' + "'new_password';" + '"')
#         sudo("psql -c 'ALTER USER new_user CREATEDB;'")
#         sudo("psql -c 'CREATE DATABASE newdb;'")
#         sudo("psql -c 'GRANT ALL PRIVILEGES ON DATABASE 'newdb' to new_user;'")
#
#     if run("nginx -v").failed:
#         sudo(" apt-get install nginx -y")

# run("python manage.py makemigrations --settings=project.settings.development")
# run("python manage.py migrate --settings=project.settings.development")
# sudo("/etc/init.d/nginx start")

# gunicorn +x

def cs():
    local('python manage.py collectstatic')
    # need to be confirmed


def pull():
    local('git pull')


def migrate():
    local('python manage.py migrate')


def deploy():
    # create needed folders if not exists
    cs()
    pull()
    migrate()
    # sudo("pip install -r requirements/production.txt")
    # restart nginx


def makemigrations():
    local('python manage.py makemigrations')


def backup():
    pass
