from fbchat import log, Client 
from fbchat.models import *
import psycopg2
import json
import time

conn = psycopg2.connect("dbname=messenger user=sp1r3")
cur = conn.cursor() 
thread_type = ThreadType.GROUP

conf = json.load(open('creds/config.json', 'r'))
timestamp=None
thread_id = conf['thread_main']
client = Client(conf['username_bobby'],conf['password_bobby'])

cur.execute("SELECT DISTINCT AUTHOR FROM MESSAGES");
users = cur.fetchall()
for user in users:
    userinfo = client.fetchUserInfo(user[0])[user[0]]
    print(userinfo.name)
    cur.execute("INSERT INTO USERS (UID, NAME, PROFILEPIC) VALUES (%s, %s, %s)", (user[0], userinfo.name, userinfo.photo))
    conn.commit()
    print(userinfo)
cur.close()
conn.close()

