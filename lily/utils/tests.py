from django.test import TestCase
from django.http.request import HttpRequest
from lily.utils.request import is_external_referer


class UtilTests(TestCase):
    def test_is_not_external_referer(self):
        request = HttpRequest()
        request.META['HTTP_REFERER'] = 'app.hellolily.nl/some-url/'

        self.assertFalse(is_external_referer(request))

    def test_is_external_referer(self):
        request = HttpRequest()
        request.META['HTTP_REFERER'] = 'app.notlily.com/some-url/'

        self.assertTrue(is_external_referer(request))
