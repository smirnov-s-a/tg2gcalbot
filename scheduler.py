from __future__ import print_function
import datetime
import requests
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']
auth_port=52179
credentials_name='credentials-web.json'

def sendMessage(chat_id, text_message):
    text_message=text_message.replace('&prompt=consent', '')
    text_message=text_message.replace('/auth/', '%3A%2F%2Fauth%3A%2F%2F')
    text_message=text_message.replace('&', '%26')
    text_message=text_message.replace('https%3A%2F%2Fwww', 'https%253A%252F%252Fwww')
    url = 'https://api.telegram.org/bot5855042022:AAECakCVuC9qFPxjO8GHXxvvstr2cKTNOd4/sendmessage?chat_id=' + str(chat_id) + '&text='+text_message
    response = requests.get(url)
    return response


def book_timeslot(booking_name, booking_date, booking_time, booking_long, booking_description, chat_id):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    user_pickle = str(chat_id) + '.token.pickle'
    if os.path.exists(user_pickle):
        with open(user_pickle, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_name, SCOPES)

            auth_url, _ = flow.authorization_url(prompt='consent')
            link_text = 'Please go to this URL: {}'.format(auth_url)
            print(link_text)
            ##sendMessage(chat_id, link_text)

            creds = flow.run_local_server(port=auth_port)

        # Save the credentials for the next run
        with open(user_pickle, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # --------------------- Manipulating Booking Time ----------------------------
    start_time = str(booking_date) + 'T' + booking_time + ':00+03:00'
    end_time_long = booking_time+booking_long
    end_time = str(booking_date) + 'T' + str(int(booking_time[:2]) + int(booking_long)) + ':00:00+03:00'
    # ----------------------------------------------------------------------------

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Booking a time slot....')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])


    # Call the Calendar API
    print('Getting list of calendars')
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])


    if not calendars:
        print('No calendars found.')
    for calendar in calendars:
        if calendar.get('primary'):
            attendee_email = calendar['id']

    print(attendee_email)
    if not events:
        event = {
            'summary': str(booking_name),
            'location': 'Moscow',
            'description': str(booking_description),
            'start': {
                'dateTime': start_time,
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Europe/Moscow',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=1'
            ],
            'attendees': [
                {'email': attendee_email},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return True

    else:
        # --------------------- Check if there are any similar start time ---------------------
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if start == start_time:
                print('Already book....')
                return False
        # -------------------- Break out of for loop if there are no apppointment that has the same time ----------
        event = {
            'summary': str(booking_name),
            'location': 'Moscow',
            'description': str(booking_description),
            'start': {
                'dateTime': start_time,
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Europe/Moscow',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=1'
            ],
            'attendees': [
               # {'email': 'automationfeed@gmail.com'},
                {'email': attendee_email},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return True


if __name__ == '__main__':
    input_email = 'test@test.ru'

    booking_time = '14:00'
    booking_date = '2024-01-01'
    booking_long = '1'
    booking_name = 'Event'
    booking_description = 'Sent from telegram'
    chat_id = '0'
    result = book_timeslot(booking_name, booking_date, booking_time, booking_long, booking_description, chat_id)