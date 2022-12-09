from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from accounts.utils import process_charges
from django.utils import timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.db.models import Q
import os
from accounts.models import Customer

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1DxlOpctqoIeeTdiLWb1np2BVnk3gyVnSoVRsHBqNthc"
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

    def upload(self, creds: Credentials):
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        data: list[list] = []
        for customer in Customer.objects.filter(~(Q(user=None))):
            data.append(
                [
                    customer.customerID,
                    customer.customer_aws_account_id,
                    customer.product_code,
                    customer.user.first_name,
                    customer.user.last_name,
                    customer.user.email,
                ]
            )
        sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="A2:F").execute()
        sheet.values().append(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, range='A2:F2', valueInputOption='USER_ENTERED', body={'values': data}
        ).execute()

        

    def read(self, creds: Credentials):
        try:
            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
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
        creds: Credentials = self.authorize()
        self.upload(creds)
        
        self.stdout.write(self.style.SUCCESS("Ended Charges processing."))
        self.stdout.write(self.style.SUCCESS('Current Time: "%s"' % timezone.now()))
