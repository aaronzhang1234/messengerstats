#! env/bin/python3

from graph_maker import Grapher
from fbchat import Client
import json
from fbchat.models import *
import urllib.request
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload
import os


SCOPES = 'https://www.googleapis.com/auth/drive'

store = file.Storage('creds/token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('creds/drivecreds.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

thread_type = ThreadType.GROUP

#grapherson = Grapher()
#grapherson.graph_of_messages(timespan="day")
#photo_name = grapherson.wordcloud(timespan = "day", show_names = False)
#print(photo_name)

photo_name = "wordcloud(2018-Oct-30).png"
folderid = '1qO9CXijYdUWL_efZZy9YlOWziOhnrlWY'
file_metadata = {
    'name': photo_name,
    'parents':[folderid]
}
media = MediaFileUpload('photos/' +photo_name,
                        mimetype='image/png')
file= service.files().create(body=file_metadata,
                                   media_body=media,
                                   fields='id').execute()
