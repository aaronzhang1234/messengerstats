from fbchat import log, Client
from listener import CustomClient
import json


conf = json.load(open('creds/config.json', 'r'))
client = CustomClient(conf['username_aaron'],conf['password_aaron'])
client.listen()

