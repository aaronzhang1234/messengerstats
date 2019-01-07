import re
import os
from datetime import datetime, time, timedelta
import time as t
import psycopg2
import textstat
from wordcloud import WordCloud
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

conn = psycopg2.connect("dbname=messenger user=sp1r3")
cur = conn.cursor()

class Grapher():
    def wordcloud(self, for_users=False, timespan=''):
        os.system('rm photos/*.png')
        dumb_words = open("dumbwords.txt", "r")
        date_start= self.get_dates(timespan)
        query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND TIMESTAMP > %s") 
        cur.execute(query, (date_start, ))
        texts = cur.fetchall() 
        total_words = ""
        for text in texts:
            total_words = total_words + " " + text[0] 
        total_words = re.sub(r"https\S+", "", total_words)
        for dumb_word in dumb_words:
            total_words = total_words.replace(" "+dumb_word.rstrip()+" ", " ")
            total_words = total_words.replace("Yeah ", "")
        wordcloud = WordCloud().generate(total_words)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig('photos/today.png')
        if for_users:
            query = ("SELECT DISTINCT AUTHOR, NAME FROM MESSAGES LEFT JOIN USERS ON USERS.UID=MESSAGES.AUTHOR AND TIMESTAMP > %s ")
            cur.execute(query, (date_start,))
            users = cur.fetchall()
            for user in users:
               if user[1]:
                   print("Starting " + user[1])
                   query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND AUTHOR=%s AND TIMESTAMP > %s")
                   cur.execute(query, (user[0], date_start))
                   texts = cur.fetchall()
                   total_words = 'fuck '
                   for text in texts:
                      total_words = total_words + " " + text[0] 
                   total_words = re.sub(r"https\S+", "", total_words)
                   for dumb_word in dumb_words:
                       total_words = total_words.replace(" "+dumb_word.rstrip()+" ", " ")
                       total_words = total_words.replace("Yeah ", "")
                   wordcloud = WordCloud().generate(total_words)
                   plt.imshow(wordcloud, interpolation='bilinear')
                   plt.axis("off")
                   plt.savefig('photos/' + user[1] + '.png')
                   dumb_words.seek(0)
    def flesch(self):
        query = ("SELECT NAME,UID FROM USERS")
        cur.execute(query)
        users = cur.fetchall()
        for user in users:
           query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND AUTHOR=%s")
           cur.execute(query, (user[1], ))
           texts = cur.fetchall()
           total_flesch = 0
           num_tuples = len(texts)
           for text in texts:
               total_flesch = total_flesch + textstat.flesch_kincaid_grade(text[0]+".")
           average_flesch = total_flesch / num_tuples
           print(user[0] +"'s Flesch is " + str(average_flesch))
    def get_dates(self, timespan = ''):
        date_start = 0
        p = '%Y-%m-%d %H:%M:%S'
        current_time = datetime.today().replace(microsecond=0)
        if timespan == 'hour':
            last_midnight_datetime = str(current_time - timedelta(hours=1))
        if timespan == 'day':
            last_midnight_datetime = str(current_time - timedelta(days=1))
        if timespan =='week':
            last_midnight_datetime = str(current_time - timedelta(weeks=1))
        if timespan =='month':
            last_midnight_datetime = str(current_time - timedelta(weeks=4))
        print(last_midnight_datetime)
        date_start = int(t.mktime(t.strptime(last_midnight_datetime, p)))
        return date_start

