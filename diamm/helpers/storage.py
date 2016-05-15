import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# From https://gist.github.com/fabiomontefuscolo/1584462
class OverwriteStorage(FileSystemStorage):
    """
        Overwrites a file of the same name instead of trying to append underscores
        until the name doesn't match.
    """
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
