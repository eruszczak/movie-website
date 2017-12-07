from os import makedirs
from os.path import join, exists
from uuid import uuid4

import requests
from django.core.exceptions import ValidationError
# from django.core.mail import mail_admins


# def send_email(subject, message):
#     mail_admins(
#         subject,
#         message,
#         # html_message=message,
#     )


def get_instance_file_path(instance, file_name):
    folder_path = instance.get_folder_path()
    return join(folder_path, file_name)


def get_random_file_path(instance, file_name):
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


class SlashDict(dict):
    """
    Dict which allows you to get nested values like this: d['key1/key2']
    https://stackoverflow.com/a/31034040/5821316
    """

    def __getitem__(self, key):
        key = key.split('/')
        if len(key) == 1:
            return dict.__getitem__(self, key[0])

        # assume that the key is a list of recursively accessible dicts
        def get_one_level(key_list, level, d):
            if level >= len(key_list):
                if level > len(key_list):
                    raise IndexError
                return d[key_list[level-1]]
            return get_one_level(key_list, level+1, d[key_list[level-1]])

        return get_one_level(key, 1, self)


def get_json_response(url, qs):
    r = requests.get(url, params=qs)
    if r.status_code == requests.codes.ok:
        return r.json()
    return None
