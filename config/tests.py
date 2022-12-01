

import os
import shutil
from pathlib import Path
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from django.contrib.staticfiles.finders import find


TEST_MEDIA_ROOT: Path = settings.BASE_DIR/ 'test-media/'

print('Test Media Root', TEST_MEDIA_ROOT)

@override_settings(STATICFILES_STORAGE='whitenoise.storage.CompressedStaticFilesStorage')
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CustomTestClass(TestCase):
    def setUp(self):
        if not TEST_MEDIA_ROOT.exists():
            os.makedirs(TEST_MEDIA_ROOT)
        super().setUp()
        
    def tearDown(self):
        if  TEST_MEDIA_ROOT.exists():
            shutil.rmtree(TEST_MEDIA_ROOT)
        super().tearDown()


def createImage(image_path: str = None) -> SimpleUploadedFile:
    """Create and return a simple uploaded file"""

    if not image_path:
        image_path = find("test_image.png", all=False)
        if not image_path:
            raise Exception("Test ImageFile not Found: test_image.jpg")
    from django.db.models.fields.files import ImageFieldFile
    #return InMemoryUploadedFile(file=open(image_path, 'rb'))
    return SimpleUploadedFile(
        name="test_image.jpg",
        content=open(image_path, "rb").read(),
        content_type="image/jpeg",
    )