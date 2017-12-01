from os import makedirs
from os.path import join, exists
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.mail import mail_admins


def send_email(subject, message):
    mail_admins(
        subject,
        message,
        # html_message=message,
    )


def get_file_path(instance, file_name):
    folder_path = instance.get_folder_path()
    extension = file_name.split('.')[1]
    random_file_name = f'{str(uuid4().hex)}.{extension}'
    return join(folder_path, random_file_name)


def validate_file_ext(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Only csv files are supported')


def create_instance_folder(instance):
    directory = instance.get_folder_path(absolute=True)
    if not exists(directory):
        makedirs(directory)
