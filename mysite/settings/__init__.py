from sys import platform

is_production = platform == 'linux'  # os.environ.get('ENV') or from .env


if is_production:
    from mysite.settings.settings_production import *
else:
    from mysite.settings.settings_local import *
