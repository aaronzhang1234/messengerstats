from fbchat import log, Client
from listener import CustomClient
import json


thread_type = ThreadType.GROUP
conf = json.load(open('creds/config.json', 'r'))
client = CustomClient(conf['username_bobby'],conf['password_bobby'])
client.listen()

