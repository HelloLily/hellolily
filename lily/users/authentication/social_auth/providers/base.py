import requests
from django.conf import settings
from django.core.files.base import ContentFile


class BaseAuthProvider(object):
    def get_picture(self, session, url):
        picture = ''
        if url:
            response = session.get(url)
            if response.status_code == requests.codes.ok:
                extension = response.headers.get('Content-Type', '/').split('/')[-1]

                if extension:
                    picture = ContentFile(
                        content=response.content,
                        name='profile-picture.{}'.format(extension)
                    )

        return picture

    def get_language(self, locale):
        language = ''

        try:
            language_code = locale.split('-')[-1].lower()
            language = language_code if language_code in [l[0] for l in settings.LANGUAGES] else ''
        except (AttributeError, IndexError):
            pass

        return language
