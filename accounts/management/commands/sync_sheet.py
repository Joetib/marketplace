from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from accounts.utils import process_charges
from django.utils import timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from accounts.utils import update_customer_entitlement
from django.db.models import Q
import os
from accounts.models import Customer
from django.conf import settings
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID =  settings.SPREADSHEET_ID 
SAMPLE_RANGE_NAME = 'A2:F'


class Command(BaseCommand):
    help = "Sends charges data to aws marketplace"

    def authorize(self) -> Credentials:
        self.stdout.write(self.style.SUCCESS("Signing into Google account"))

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            self.stdout.write(
                self.style.WARNING(
                    "Could not find authorization File."
                    " Opening brower for manual login."
                )
            )

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds
    
    def update_customers(self):
        self.stdout.write(self.style.SUCCESS("Updating customer entitlements"))
        for customer in Customer.objects.all():
            update_customer_entitlement(customer)
        self.stdout.write(self.style.SUCCESS("Completed Updating customer entitlements"))

    def upload(self, creds: Credentials):
        self.stdout.write(self.style.SUCCESS("Start: Uploading spreadsheet content."))
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        data: list[list] = []
        for customer in Customer.objects.filter(~(Q(user=None))):
            date = ''
            if customer.expiry_date:
                date = str(customer.expiry_date)
            data.append(
                [
                    customer.customerID,
                    customer.customer_aws_account_id,
                    customer.product_code,
                    customer.dimension,
                    float(customer.value),
                    date,
                    customer.user.first_name,
                    customer.user.last_name,
                    customer.user.email,
                ]
            )
        sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range="A2:H").execute()
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID, range='A2:H', valueInputOption='USER_ENTERED', body={'values': data}
        ).execute()
        self.stdout.write(self.style.SUCCESS("Done: Uploading spreadsheet content."))

        

    def read(self, creds: Credentials):
        try:
            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])

            if not values:
                print('No data found.')
                return

            print('Name, Major:')
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                print('%s, %s' % (row[0], row[4]))
        except HttpError as err:
            print(err)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Current Time: "%s"' % timezone.now()))
        self.update_customers()
        creds: Credentials = self.authorize()
        self.upload(creds)
        
        self.stdout.write(self.style.SUCCESS("Ended SpreadSheet processing."))
        self.stdout.write(self.style.SUCCESS('Current Time: "%s"' % timezone.now()))
