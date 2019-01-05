from fbchat import log, Client
from fbchat.models import *
import psycopg2
import json

thread_type = ThreadType.GROUP

conn = psycopg2.connect("dbname=messenger user=sp1r3")
cur = conn.cursor() 

conf = json.load(open('creds/config.json', 'r'))
timestamp=None
thread_id = conf['thread_main']
client = Client(conf['username_bobby'],conf['password_bobby'])
messages = client.fetchThreadMessages(thread_id = thread_id, limit=200, before=timestamp)

while len(messages)>=2:
    messages = client.fetchThreadMessages(thread_id = thread_id, limit=200, before=timestamp)
    messages = messages[1:]
    for message_object in messages:
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
    messages.reverse()
    timestamp = messages[0].timestamp
print("Finished!")
cur.close()
conn.close()

