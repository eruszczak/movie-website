from os import makedirs
from os.path import join, exists
from uuid import uuid4

import requests


def get_random_file_path(instance, file_name):
    folder_path = instance.get_folder_path(create=True)
    extension = file_name.split('.')[1]
    random_file_name = f'{str(uuid4().hex)}.{extension}'
    return join(folder_path, random_file_name)


def create_folder_if_not_exists(directory):
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
        return r.json(), r.url
    return None


def get_list_duplicates(seq):
    """
    a = [1,2,3,2,1,5,6,5,5,5]
    list_duplicates(a) # yields [1, 2, 5]
    """
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set(x for x in seq if x in seen or seen_add(x))
    return list(seen_twice)
