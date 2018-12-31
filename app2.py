from fbchat import log, Client 
from fbchat.models import *
import psycopg2
import json
import time

conn = psycopg2.connect("dbname=messenger user=sp1r3")
cur = conn.cursor() 
thread_type = ThreadType.GROUP

conf = json.load(open('config.json', 'r'))
timestamp=None
thread_id = conf['thread_banana']
client = Client(conf['username_bobby'],conf['password_bobby'])

#client.send(Message(text='fug'), thread_id=thread_id, thread_type=thread_type)
messages = client.fetchThreadMessages(thread_id = thread_id, limit=200, before=timestamp)

#for message in messages:
#    attachments = message.attachments
#    text = None
#    if message.text==None and len(attachments)<1:
#        print("event")
#    else:
#        if len(attachments)>=1:                
#            attached_urls = []
#            for attachment in attachments:
#                attach_type = type(attachment)
#                if attach_type is AudioAttachment:
#                    attach_url = attachment.url
#                    attached_urls.append(attach_url)
#                elif attach_type is FileAttachment:
#                    attach_url = attachment.url
#                    attached_urls.append(attach_url)
#                elif attach_type is ImageAttachment:
#                    attach_url = attachment.preview_url
#                    attached_urls.append(attach_url) 
#            attached_urls_text = '\n'.join(attached_urls)
#            text = attached_urls_text
#        else:
#            text = message.text
#        print(text)
while len(messages)>=2:
    messages = client.fetchThreadMessages(thread_id = thread_id, limit=200, before=timestamp)
    messages = messages[1:]
    for message in messages:
        attachments = message.attachments
        text = None
        if message.text==None and len(attachments)<1:
            print("event")
        else:
            if len(attachments)>=1:                
                attached_urls = []
                for attachment in attachments:
                    attach_type = type(attachment)
                    if attach_type is AudioAttachment:
                        attach_url = attachment.url
                        attached_urls.append(attach_url)
                    elif attach_type is FileAttachment:
                        attach_url = attachment.url
                        attached_urls.append(attach_url)
                    elif attach_type is ImageAttachment:
                        attach_url = attachment.preview_url
                        attached_urls.append(attach_url) 
                    elif attach_type is VideoAttachment:
                        attach_url = attachment.preview_url
                        attached_urls.append(attach_url)
                    elif attach_type is Sticker:
                        attach_url = attachment.url
                        attached_urls.append(attach_url)
                attached_urls_text = '\n'.join(attached_urls)
                text = attached_urls_text
            else:
                text = message.text
            print(text)
            cur.execute("INSERT INTO MESSAGES (MESSAGEID, TEXT, AUTHOR,THREADID, TIMESTAMP) values (%s,%s,  %s, %s, %s);", (message.uid, text, message.author, thread_id, message.timestamp))
            conn.commit()
    messages.reverse()
    timestamp = messages[0].timestamp
    print(len(messages))
cur.close()
conn.close()

