import os

debug = os.environ.get('DEBUG', 'False') == 'True'

if debug:
    from .settings_local import *
else:
    from .settings_production import *
