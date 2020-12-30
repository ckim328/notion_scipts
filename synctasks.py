import datetime
import pickle
import os.path
import requests
from notion.client import NotionClient
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#### depends how your notion page is organized, and how you layout tasks

SCOPES = ['https://www.googleapis.com/auth/tasks']

def main():

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    client = NotionClient(
        token_v2="YOUR_NOTION_TOKEN")
    if os.path.exists('tokenTasks.pickle'): 
        with open('tokenTasks.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials(2).json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('tokenTasks.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('tasks', 'v1', credentials=creds)

    # Call the Tasks API
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])

    id_list = ''
    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print(u'{0} ({1})'.format(item['title'], item['id']))
            id_list = item['id']
    notionEvents = getNotionEvents(client)
    today = datetime.datetime.now()
    today = str(today)[:10]

    createGoogleTasks(service,id_list,notionEvents)

# ------------------GOOGLES' API
def createGoogleTasks(service,tasklistId,events):
    for i in events:
        task = {
            "title": i,
        }
        event = service.tasks().insert(tasklist=tasklistId,body=task).execute()
        print('Task created: %s' % (event.get('htmlLink')))
        
# ------------------NOTION'S API

def getNotionEvents(client):
    coll = client.get_collection_view(
        'NOTION_PAGE_URL')
    # res = {} # uncomment if you want to include titles for your tasks,
    # some edits will have to be made to createGoogleTasks(...)
    entries = coll.collection.get_rows()
    temp = entries[0].get()
    #grabs latest to do list
    page = client.get_block(temp['id'])
    todo_list = []
    for i in page.children:
        todo_list.append(i.title)
    return todo_list

if __name__ == '__main__':
    main()
