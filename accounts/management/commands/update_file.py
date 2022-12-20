from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone 
from django.conf import settings


class Command(BaseCommand):
    help = "Sends charges data to aws marketplace"


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Current Time: "%s"' % timezone.now()))
        self.stdout.write(self.style.SUCCESS('Updating the file'))
        with open(settings.BASE_DIR / "file.txt", 'a') as f:
            f.write(f"\nCurrent time {timezone.now()}")
        self.stdout.write(self.style.SUCCESS('Current Time: "%s"' % timezone.now()))
