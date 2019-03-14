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

abs_path = '/Users/sp1r3/Documents/projects/websites/messenger'
SCOPES = 'https://www.googleapis.com/auth/drive'


store = file.Storage(abs_path + 'creds/token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(abs_path + 'creds/drivecreds.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

grapherson = Grapher()
frequency_name = grapherson.graph_of_messages(timespan="day")
wordcloud_name = grapherson.wordcloud(timespan = "day", show_names = False)
print(wordcloud_name)
print(frequency_name)

folderid = '1qO9CXijYdUWL_efZZy9YlOWziOhnrlWY'
wordcloud_metadata = {
    'name': wordcloud_name,
    'parents':[folderid]
}
frequency_metadata = {
    'name': frequency_name,
    'parents':[folderid]
}

wordcloud = MediaFileUpload(abs_path + 'photos/' +wordcloud_name,
                        mimetype='image/png')
file= service.files().create(body=wordcloud_metadata,
                                   media_body=wordcloud,
                                   fields='id').execute()

frequency = MediaFileUpload(abs_path + 'photos/' +frequency_name,
                        mimetype='image/png')
file= service.files().create(body=frequency_metadata,
                                   media_body=frequency,
                                   fields='id').execute()


