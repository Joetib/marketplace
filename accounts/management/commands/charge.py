from django.core.management.base import BaseCommand, CommandError
from accounts.utils import process_charges
from django.utils import timezone
class Command(BaseCommand):
    help = 'Sends charges data to aws marketplace'

    

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Current Time: "%s"'%  timezone.now()))
        process_charges()
        self.stdout.write(self.style.SUCCESS("Ended Charges processing."))
        self.stdout.write(self.style.SUCCESS('Current Time: "%s"'%  timezone.now()))