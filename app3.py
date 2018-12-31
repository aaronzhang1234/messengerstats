from __future__ import print_function
from fbchat import log, Client 
from fbchat.models import *
import psycopg2
import json
import os
import time
import urllib.request
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('drivecreds.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

thread_type = ThreadType.GROUP

conf = json.load(open('config.json', 'r'))
timestamp=None
thread_id = conf['thread_main']
client = Client(conf['username_bobby'],conf['password_bobby'])
messages = client.fetchThreadMessages(thread_id = thread_id, limit=200, before=timestamp)
while len(messages)>=2:
    messages = client.fetchThreadMessages(thread_id = thread_id, limit=200, before=timestamp)
    messages = messages[1:]
    for message in messages:
        attachments = message.attachments
        text = None
        if message.text==None and len(attachments)<1:
            memes='dreams'
        else:
            if len(attachments)>=1:                
                attached_urls = []
                num = 1
                for attachment in attachments:
                    attach_type = type(attachment)
                    if attach_type is AudioAttachment:
                        attach_url = attachment.url
                    elif attach_type is FileAttachment:
                        attach_url = attachment.url
                    elif attach_type is ImageAttachment:
                        image = client.fetchImageUrl(attachment.uid)
                        print(image)
                        name = str(attachment.uid)+'.png'
                        folderid = '1H0uoAKMJca7mZNVuDqMKPUhO9oMtLdeJ'
                        urllib.request.urlretrieve(image, "photos/" + name)
                        file_metadata = {
                            'name': name,
                            'parents':[folderid]
                        }
                        media = MediaFileUpload('photos/' +name,
                                                mimetype='image/png')
                        file= service.files().create(body=file_metadata,
                                                           media_body=media,
                                                           fields='id').execute()
                        os.remove('photos/'+name)
                    elif attach_type is VideoAttachment:
                        attach_url = attachment.preview_url
                    elif attach_type is Sticker:
                        attach_url = attachment.url
                attached_urls_text = '\n'.join(attached_urls)
                text = attached_urls_text
    messages.reverse()
    timestamp = messages[0].timestamp

