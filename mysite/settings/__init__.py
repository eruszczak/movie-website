from decouple import config


debug = config('DEBUG', default=False, cast=bool)

if debug:
    from .settings_local import *
else:
    from .settings_production import *
