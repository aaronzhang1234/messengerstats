from fbchat import log, Client
from fbchat.models import *
import psycopg2
import json
import time

conn = psycopg2.connect("dbname=messenger user=sp1r3")
cur = conn.cursor() 
thread_type = ThreadType.GROUP

class CustomClient(Client):
    def onPeopleAdded(self, added_ids, author_id, thread_id, **kwargs):
        current_time = time.clock_gettime(0)
        for added_id in added_ids:
            cur.execute("INSERT INTO CaG (UID, THREAD_ID, TIMESTAMP, GOING) values (%s, %s, %s, %s);", (added_id, thread_id, current_time, False))
            conn.commit()
    def onPersonRemoved(self, removed_id, author_id, thread_id, **kwargs):
        current_time = time.clock_gettime(0)
        cur.execute("INSERT INTO CaG (UID, THREAD_ID, TIMESTAMP, GOING) values (%s, %s, %s, %s);", (removed_id, thread_id, current_time, True))
        conn.commit()
    def onMessageSeen(self, seen_by, thread_id, thread_type, seen_ts, ts, metadata, msg):
        self.addUser(seen_by)
    def onMessage(self, mid, author_id, message_object, thread_id, thread_type, ts, metadata, msg, **kwargs):
        self.addUser(author_id)
        uid = message_object.uid
        author = message_object.author
        threadid = metadata['threadKey']['threadFbId']
        timestamp = int(message_object.timestamp)/1000
        if len(message_object.attachments)>=1:
            image_urls = []
            for image in message_object.attachments:
                image_urls.append(image.preview_url) 
            image_urls_text = '\n'.join(image_urls)
            cur.execute("INSERT INTO messages(messageid, text, author, threadid, timestamp) VALUES (%s, %s, %s, %s, %s);", (uid, image_urls_text, author, threadid, timestamp))
            conn.commit() 
        else:
            text = message_object.text
            if text=='disco':
                self.disco_time(threadid)
            cur.execute("INSERT INTO messages(messageid, text, author, threadid, timestamp) VALUES (%s, %s, %s, %s, %s);", (uid, text, author, threadid, timestamp))
            conn.commit() 
    def addUser(self, uid):    
        cur.execute("SELECT name FROM users WHERE uid = %s;", (uid,))
        user = cur.fetchone()
        if not user:
            user = self.fetchUserInfo(uid)[uid]
            cur.execute("INSERT INTO USERS(uid, name, profilepic) VALUES (%s, %s, %s);", (user.uid, user.name, user.photo))
            conn.commit()
    def disco_time(self, thread_id):
        colors = [ThreadColor.BILOBA_FLOWER,
                  ThreadColor.MESSENGER_BLUE, 
                  ThreadColor.VIKING,
                  ThreadColor.GOLDEN_POPPY,
                  ThreadColor.RADICAL_RED, 
                  ThreadColor.SHOCKING,
                  ThreadColor.PICTON_BLUE,
                  ThreadColor.FREE_SPEECH_GREEN,
                  ThreadColor.PUMPKIN,
                  ThreadColor.LIGHT_CORAL,
                  ThreadColor.MEDIUM_SLATE_BLUE,
                  ThreadColor.DEEP_SKY_BLUE,
                  ThreadColor.FERN, 
                  ThreadColor.CAMEO, 
                  ThreadColor.BRILLIANT_ROSE]
        for color in colors:
            self.changeThreadColor(color, thread_id)            

conf = json.load(open('config.json', 'r'))
client = CustomClient(conf['username'],conf['password'])
client.listen()
cur.close()
conn.close()
messages = client.fetchThreadMessages(thread_id = thread_id, limit=200)
#client.send(Message(text='fug'), thread_id=thread_id, thread_type=thread_type)
