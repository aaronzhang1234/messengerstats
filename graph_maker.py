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
        date_start, date_end = self.get_dates(timespan)
        query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND TIMESTAMP > %s AND TIMESTAMP <%s") 
        cur.execute(query, (date_start, date_end))
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
            query = ("SELECT DISTINCT AUTHOR, NAME FROM MESSAGES LEFT JOIN USERS ON USERS.UID=MESSAGES.AUTHOR AND TIMESTAMP > %s AND TIMESTAMP < %s")
            cur.execute(query, (date_start, date_end))
            users = cur.fetchall()
            for user in users:
               if user[1]:
                   print("Starting " + user[1])
                   query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND AUTHOR=%s AND TIMESTAMP > %s AND TIMESTAMP < %s ")
                   cur.execute(query, (user[0], date_start, date_end))
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
    def piechart(self):
        cur.execute('SELECT NAME, COUNT(DISTINCT MESSAGES.UID) FROM MESSAGES RIGHT JOIN USERS ON MESSAGES.AUTHOR=USERS.UID WHERE THREAD_ID=%s GROUP BY NAME ORDER BY COUNT(DISTINCT MESSAGES.UID) DESC', (conf["thread_main"],));
        messagesent = cur.fetchall()
        names = []
        numsent = []
        for msg in messagesent:
            names.append(msg[0])
            numsent.append(msg[1])
        fig1, ax1 = plt.subplots()
        wedges, texts = ax1.pie(numsent, shadow=True, startangle=90)
        ax1.legend(wedges, names,
                   title="Users",
                   loc="center left",
                   bbox_to_anchor=(1,0, 2, 0))
        ax1.set_title("Messenger Stats")
        ax1.axis('equal')
        plt.show()
    def get_dates(self, timespan = ''):
        print(timespan)
        date_start = 0
        date_end = 2000000000
        p = '%Y-%m-%d %H:%M:%S'
        if timespan == 'day':
            midnight_date = datetime.combine(datetime.today(), time.min)
            last_midnight_datetime = str(midnight_date - timedelta(days=1))
            date_start = int(t.mktime(t.strptime(last_midnight_datetime, p)))
            date_end = int(t.mktime(t.strptime(str(midnight_date), p)))
        if timespan =='week':
            midnight_date = datetime.combine(datetime.today(), time.min)
            last_midnight_datetime = str(midnight_date - timedelta(weeks=1))
            date_start = int(t.mktime(t.strptime(last_midnight_datetime, p)))
            date_end = int(t.mktime(t.strptime(str(midnight_date), p)))
        if timespan =='month':
            midnight_date = datetime.combine(datetime.today(), time.min)
            last_midnight_datetime = str(midnight_date - timedelta(weeks=4))
            date_start = int(t.mktime(t.strptime(last_midnight_datetime, p)))
            date_end = int(t.mktime(t.strptime(str(midnight_date), p)))
        return date_start,date_end

