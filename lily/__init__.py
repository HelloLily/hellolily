from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app  # noqa

# Semver versioning.
VERSION = (0, 4, 30)
__version__ = '.'.join(map(str, VERSION))

default_app_config = 'lily.app.LilyConfig'
