from fbchat import log, Client
from fbchat.models import *
import psycopg2
import json
import time

thread_type = ThreadType.GROUP
conn = psycopg2.connect("dbname=messenger user=sp1r3")
cur = conn.cursor()
class CustomClient(Client):
    def onPeopleAdded(self, added_ids, author_id, thread_id, **kwargs):
        for added_id in added_ids:
            cur.execute("SELECT * FROM ACCESS WHERE UID=%s AND THREAD_ID = %s;", (added_id, thread_id))
            user = cur.fetchone()
            if user:
                cur.execute("UPDATE ACCESS SET IS_IN='1' WHERE UID=%s AND THREAD_ID = %s", (added_id, thread_id))
                conn.commit()
    def onPersonRemoved(self, removed_id, author_id, thread_id, **kwargs):
        cur.execute("SELECT * FROM ACCESS WHERE UID=%s AND THREAD_ID = %s;", (author_id, thread_id))
        user = cur.fetchone()
        if user:
            cur.execute("UPDATE ACCESS SET IS_IN='0' WHERE UID=%s AND THREAD_ID = %s", (author_id, thread_id))
            conn.commit()
    def onTitleChange(self, mid, author_id, new_title, thread_id, thread_type, ts, metadata, msg):
        cur.execute("SELECT * FROM THREADS WHERE THREAD_ID = %s", (thread_id,))
        is_thread = cur.fetchone()
        if is_thread:
            cur.execute("UPDATE THREADS SET THREAD_NAME=%s WHERE THREAD_ID=%s", (new_title, thread_id))
            conn.commit()
    def onMessageSeen(self, seen_by, thread_id, thread_type, seen_ts, ts, metadata, msg):
        self.addUser(seen_by)
    def onMessage(self, mid, author_id, message_object, thread_id, thread_type, ts, metadata, msg, **kwargs):
        if thread_type == ThreadType.USER:
            cur.execute("SELECT * FROM ACCESS WHERE UID=%s", (author_id,))
            user = cur.fetchone()
            if user:
                if message_object.text == "!help":
                    self.send(Message(text="Commands!\n '!join <server id>' to join servers\n '!show' to show available servers"), thread_id = author_id, thread_type = ThreadType.USER)
                if message_object.text == "!show":
                    cur.execute("SELECT THREAD_NAME, THREADS.THREAD_ID FROM ACCESS LEFT JOIN THREADS ON THREADS.THREAD_ID = ACCESS.THREAD_ID WHERE UID=%s", (author_id, ))
                    threads = cur.fetchall()
                    show_list = ["Here are the servers you can join!", "Server Name | Server ID", "~~~~~~~~~~~~~~~~~~"]
                    for thread in threads:
                        show_list.append(thread[0] + " | " + thread[1])
                    show_msg = "\n".join(show_list)
                    self.send(Message(text=show_msg), thread_id = author_id, thread_type = ThreadType.USER)
                if message_object.text[:5] == "!join":
                    server_id = message_object.text[6:]
                    cur.execute("SELECT * FROM ACCESS WHERE UID = %s AND THREAD_ID = %s", (author_id, server_id))
                    is_allowed = cur.fetchone()
                    if is_allowed:
                        print(server_id)
                        try:
                            self.addUsersToGroup([author_id], server_id)
                        except FBchatFacebookError:
                            self.send(Message(text="Something went wrong, you're probably already in this chat"), thread_id = author_id, thread_type=ThreadType.USER)
                    else:
                        self.send(Message(text="You are not allowed into this chat"), thread_id = author_id, thread_type=ThreadType.USER)
        else:
            self.addUser(author_id)
            attachments = message_object.attachments
            message_timestamp = int(message_object.timestamp)/1000
            message_author = message_object.author
            message_uid = message_object.uid
            if message_object.text!=None or len(attachments)>=1: 
                if len(attachments)>=1: 
                    for attachment in attachments:
                        attach_url = ""
                        attach_type = type(attachment)
                        attachment_id = attachment.uid
                        if attach_type is AudioAttachment or attach_type is FileAttachment or attach_type is Sticker:
                            attach_url = attachment.url
                            query = "INSERT INTO MESSAGES (UID, AUTHOR, THREAD_ID, IS_MEDIA, ATTACHMENT_ID, ATTACHMENT_LINK, TIMESTAMP) values (%s, %s, %s, %s, %s, %s, %s);"
                            cur.execute(query, (message_uid, message_author, thread_id, 'F', attachment_id, attach_url, message_timestamp))
                        elif attach_type is ImageAttachment or attach_type is VideoAttachment:
                            attach_url = attachment.preview_url
                            query = "INSERT INTO MESSAGES (UID, AUTHOR, THREAD_ID, IS_MEDIA, ATTACHMENT_ID, ATTACHMENT_LINK, TIMESTAMP) values (%s, %s, %s, %s, %s, %s, %s);"
                            cur.execute(query, (message_uid, message_author, thread_id, 'T', attachment_id, attach_url, message_timestamp))
                        conn.commit()
                else:
                    text = message_object.text
                    query = "INSERT INTO MESSAGES (UID, TEXT, AUTHOR, THREAD_ID, TIMESTAMP) values (%s, %s, %s, %s, %s);"
                    cur.execute(query, (message_uid, text, message_author, thread_id, message_timestamp))
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

