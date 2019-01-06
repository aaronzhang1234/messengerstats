from graph_maker import Grapher
from fbchat import Client
import json
from fbchat.models import *

thread_type = ThreadType.GROUP

grapherson = Grapher()
grapherson.wordcloud(timespan='day')
conf = json.load(open('creds/config.json', 'r'))
client = Client(conf['username'],conf['password'])
client.sendLocalImage('photos/today.png', message= Message(text='oef'), thread_id=conf['thread_bobby'], thread_type=thread_type)


