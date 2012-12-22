import os

from django.conf import settings
from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import BaseFinder
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from django.utils.datastructures import SortedDict


class GeneratedMediaFinder(BaseFinder):
    """
    A static files finder that uses the ``GENERATED_MEDIA_DIRS`` setting
    to locate files.
    """
    def __init__(self, apps=None, *args, **kwargs):
        # List of locations with static files
        self.locations = []
        # Maps dir paths to an appropriate storage instance
        self.storages = SortedDict()
        if not isinstance(settings.GENERATED_MEDIA_DIRS, (list, tuple)):
            raise ImproperlyConfigured(
                "Your STATICFILES_DIRS setting is not a tuple or list; "
                "perhaps you forgot a trailing comma?")
        for root in settings.GENERATED_MEDIA_DIRS:
            if isinstance(root, (list, tuple)):
                prefix, root = root
            else:
                prefix = ''
            if os.path.abspath(settings.STATIC_ROOT) == os.path.abspath(root):
                raise ImproperlyConfigured(
                    "The GENERATED_MEDIA_DIRS setting should "
                    "not contain the STATIC_ROOT setting")
            if (prefix, root) not in self.locations:
                self.locations.append((prefix, root))
        for prefix, root in self.locations:
            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = prefix
            self.storages[root] = filesystem_storage
        super(GeneratedMediaFinder, self).__init__(*args, **kwargs)

    def find(self, path, all=False):
        """
        Looks for files in the extra locations
        as defined in ``GENERATED_MEDIA_DIRS``.
        """
        matches = []
        for prefix, root in self.locations:
            matched_path = self.find_location(root, path, prefix)
            if matched_path:
                if not all:
                    return matched_path
                matches.append(matched_path)
        return matches

    def find_location(self, root, path, prefix=None):
        """
        Finds a requested static file in a location, returning the found
        absolute path (or ``None`` if no match).
        """
        if prefix:
            prefix = '%s%s' % (prefix, os.sep)
            if not path.startswith(prefix):
                return None
            path = path[len(prefix):]
        path = safe_join(root, path)
        if os.path.exists(path):
            return path

    def list(self, ignore_patterns):
        """
        List all files in all locations.
        """
        for prefix, root in self.locations:
            storage = self.storages[root]
            for path in utils.get_files(storage, ignore_patterns):
                yield path, storage