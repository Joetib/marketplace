from django.test import TestCase, override_settings
from config.tests import CustomTestClass, TEST_MEDIA_ROOT

@override_settings(STATICFILES_STORAGE='whitenoise.storage.CompressedStaticFilesStorage')
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestHomePage(CustomTestClass):
    """ Test to see that no exceptions are raised when trying to access the homepage"""

    def test_homepage_works_with_no_http_errors(self):
        response = self.client.get("/pages/")
        self.assertEqual(response.status_code, 200, "Homepage is not working")


@override_settings(STATICFILES_STORAGE='whitenoise.storage.CompressedStaticFilesStorage')
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestAboutPage(TestCase):
    """ Test to see that no exceptions are raised when trying to access the homepage"""

    def test_about_works_with_no_http_errors(self):
        response = self.client.get("/pages/about/")
        self.assertEqual(response.status_code, 200, "About page is not working")

