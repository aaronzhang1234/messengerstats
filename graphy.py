from graph_maker import Grapher
from fbchat import Client
import json
from fbchat.models import *
import os

thread_type = ThreadType.GROUP

os.system('rm photos/*.png')
session_cookies = {}
try:
    with open('creds/session.json','r') as f:
        session_cookies = json.load(f)
except:
    pass
grapherson = Grapher()
#print(grapherson.flesch("week"))
#grapherson.graph_of_messages(timespan="day")
grapherson.wordcloud(True, timespan = "", show_names = True)
#conf = json.load(open('creds/config.json', 'r'))
#client = Client(conf['username_kino'],conf['password_kino'], session_cookies = session_cookies)
#client.sendLocalImage('photos/today.png', message= Message(text='oef'), thread_id=conf['thread_bobby'], thread_type=thread_type)
with open('session.json','w') as f:
    json.dump(client.getSession(), f)
