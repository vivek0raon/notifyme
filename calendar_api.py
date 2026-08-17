import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

DATA_DIR = os.getenv("DATA_DIR", ".")
TOKEN_FILE = os.path.join(DATA_DIR, 'token.json')
CREDENTIALS_FILE = os.path.join(DATA_DIR, 'credentials.json')

def get_calendar_service():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"{CREDENTIALS_FILE} not found. Please download OAuth client ID credentials from Google Cloud Console and save as {CREDENTIALS_FILE}")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def add_job_event(company_name, role, deadline_str, description, calendar_id='primary'):
    """
    Creates an event in Google Calendar.
    deadline_str should be a datetime object.
    """
    service = get_calendar_service()
    if not service:
        return False

    start_time = deadline_str - datetime.timedelta(hours=1)
    
    event = {
      'summary': f'TnP Placement: {company_name} ({role})',
      'description': description,
      'start': {
        'dateTime': start_time.isoformat(),
        'timeZone': 'Asia/Kolkata',
      },
      'end': {
        'dateTime': deadline_str.isoformat(),
        'timeZone': 'Asia/Kolkata',
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 3 * 60}, # 3 hours before
          {'method': 'popup', 'minutes': 60},     # 1 hour before
        ],
      },
    }

    try:
        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Deadline event created: {event_result.get('htmlLink')}")
        return True
    except HttpError as error:
        print(f"An error occurred creating the event: {error}")
        return False

def add_instant_alert_event(company_name, role, description, calendar_id='primary'):
    """
    Creates an event scheduled for right now to trigger an immediate phone notification.
    """
    service = get_calendar_service()
    if not service:
        return False

    # Schedule the event to start 1 minute from now so it triggers an immediate reminder
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(minutes=1)
    end_time = start_time + datetime.timedelta(minutes=15)
    
    event = {
      'summary': f'🚨 NEW PLACEMENT: {company_name} ({role})',
      'description': f'A new company has arrived on the portal!\n\n{description}',
      'start': {
        'dateTime': start_time.isoformat(),
        'timeZone': 'Asia/Kolkata',
      },
      'end': {
        'dateTime': end_time.isoformat(),
        'timeZone': 'Asia/Kolkata',
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 1}, # Instantly reminds
          {'method': 'email', 'minutes': 1}, 
        ],
      },
    }

    try:
        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Instant alert created: {event_result.get('htmlLink')}")
        return True
    except HttpError as error:
        print(f"An error occurred creating the instant alert: {error}")
        return False

def add_notification_event(title, type_str, date_str, calendar_id='primary'):
    """
    Creates an event scheduled for right now to trigger an immediate phone notification for TnP notifications.
    """
    service = get_calendar_service()
    if not service:
        return False

    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(minutes=1)
    end_time = start_time + datetime.timedelta(minutes=15)
    
    event = {
      'summary': f'[{type_str}] {title}',
      'description': f'New update from TnP Portal (Posted on {date_str})',
      'start': {
        'dateTime': start_time.isoformat(),
        'timeZone': 'Asia/Kolkata',
      },
      'end': {
        'dateTime': end_time.isoformat(),
        'timeZone': 'Asia/Kolkata',
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 1},
        ],
      },
    }

    try:
        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Notification alert created: {event_result.get('htmlLink')}")
        return True
    except HttpError as error:
        print(f"An error occurred creating the notification alert: {error}")
        return False

if __name__ == "__main__":
    # Test
    # This will trigger the auth flow if token.json doesn't exist
    service = get_calendar_service()
    if service:
        print("Successfully authenticated with Google Calendar!")
