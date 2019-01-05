import re
from datetime import datetime, time
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
    last_midnight = 0
    todays_midnight = 0
    def __init__(self):
        midnight_date = str(datetime.combine(datetime.today(), time.min))
        p = '%Y-%m-%d %H:%M:%S'
        self.last_midnight = epoch = int(t.mktime(t.strptime(midnight_date, p)))
        print(self.last_midnight)
    def wordcloud(self):
        print(self.last_midnight)
        query = ("SELECT NAME,UID FROM USERS")
        dumb_words = open("dumbwords.txt", "r")
        cur.execute(query)
        users = cur.fetchall()
        for user in users:
           print("Starting " + user[0])
           query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND AUTHOR=%s")
           cur.execute(query, (user[1], ))
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
        plt.savefig("photos/"+ user[0] + '.png')
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
