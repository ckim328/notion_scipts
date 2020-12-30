import datetime
import pickle
import os.path
from notion.client import NotionClient
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    creds = None
    client = NotionClient(
        token_v2="TOKEN")
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    # now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # getGoogleEvents(service,now)
    notionEvents = getNotionEvents(client)
    # notionEvents = getNotionEvents(client)
    createGoogleEvents(service,notionEvents)

# ------------------GOOGLES' API


def getGoogleEvents(service, now):
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def createGoogleEvents(service):
    #time zone descirption attendees, loocation, reminders
    event = {
        'summary': 'To do',
        'description': 'Deciption',
        'start': {
            'dateTime': '2020-12-30T09:00:00-07:00',
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': '2020-12-30T10:00:00-10:00',
            'timeZone': 'America/New_York',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [
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

# ------------------NOTION'S API


def getNotionEvents(client):
    coll = client.get_collection_view(
        '')
    res = {}
    print(coll)
    entries = coll.collection.get_rows()
    #gets the most recently made, can be edited to grab a date
    temp = entries[0].get()
    entry_date = temp['properties']['rMVc'][0][1][0][1]['start_date']
    page = client.get_block(temp['id'])
    todo_list = []
    for i in page.children:
        todo_list.append(i.title)
    res[entry_date] = todo_list
    return res


if __name__ == '__main__':
    main()
