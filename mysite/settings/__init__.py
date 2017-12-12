from decouple import config


is_production = config('DEBUG', default=False, cast=bool)

if is_production:
    from .settings_production import *
else:
    from .settings_local import *
