from fbchat import log, Client
from fbchat.models import *
import psycopg2
from Crypto.Cipher import AES
import json
import time

thread_type = ThreadType.GROUP

conn = psycopg2.connect("dbname=messenger user=sp1r3")
cur = conn.cursor() 

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
        message.timestamp = message.timestamp/1000
        if message.text!=None or len(attachments)>=1:           
            if len(attachments)>=1:                
                for attachment in attachments:
                    attach_url = ""
                    attach_type = type(attachment)
                    if attach_type is AudioAttachment:
                        attach_url = attachment.url
                        query = "INSERT INTO MESSAGES (UID, AUTHOR, THREAD_ID, IS_MEDIA, ATTACHMENT_ID, ATTACHMENT_LINK, TIMESTAMP) values (%s, %s, %s, %s, %s, %s, %s);"
                        cur.execute(query, (message.uid, message.author, thread_id, 'F', attachment.uid, attach_url, message.timestamp))
                    elif attach_type is FileAttachment:
                        attach_url = attachment.url
                        query = "INSERT INTO MESSAGES (UID, AUTHOR, THREAD_ID, IS_MEDIA, ATTACHMENT_ID, ATTACHMENT_LINK, TIMESTAMP) values (%s, %s, %s, %s, %s, %s, %s);"
                        cur.execute(query, (message.uid, message.author, thread_id, 'F', attachment.uid, attach_url, message.timestamp))
                    elif attach_type is ImageAttachment:
                        attach_url = attachment.preview_url
                        query = "INSERT INTO MESSAGES (UID, AUTHOR, THREAD_ID, IS_MEDIA, ATTACHMENT_ID, ATTACHMENT_LINK, TIMESTAMP) values (%s, %s, %s, %s, %s, %s, %s);"
                        cur.execute(query, (message.uid, message.author, thread_id, 'T', attachment.uid, attach_url, message.timestamp))
                    elif attach_type is VideoAttachment:
                        attach_url = attachment.preview_url
                        query = "INSERT INTO MESSAGES (UID, AUTHOR, THREAD_ID, IS_MEDIA, ATTACHMENT_ID, ATTACHMENT_LINK, TIMESTAMP) values (%s, %s, %s, %s, %s, %s, %s);"
                        cur.execute(query, (message.uid, message.author, thread_id, 'T', attachment.uid, attach_url, message.timestamp))
                    elif attach_type is Sticker:
                        attach_url = attachment.url                    
                        query = "INSERT INTO MESSAGES (UID, AUTHOR, THREAD_ID, IS_MEDIA, ATTACHMENT_ID, ATTACHMENT_LINK, TIMESTAMP) values (%s, %s, %s, %s, %s, %s, %s);"
                        cur.execute(query, (message.uid, message.author, thread_id, 'F', attachment.uid, attach_url, message.timestamp))
                    conn.commit()
            else:
                text = message.text
                query = "INSERT INTO MESSAGES (UID, TEXT, AUTHOR, THREAD_ID, TIMESTAMP) values (%s, %s, %s, %s, %s);"
                cur.execute(query, (message.uid, text, message.author, thread_id, message.timestamp))
                conn.commit()
    messages.reverse()
    timestamp = messages[0].timestamp
print("Finished!")
cur.close()
conn.close()

