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
    def wordcloud(self, for_users=False, timespan='', show_names = False):
        date_start, date_now= self.get_dates(timespan)
        query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND TIMESTAMP > %s AND TIMESTAMP < %s") 
        cur.execute(query, (date_start, date_now))
        texts = cur.fetchall() 
        total_words = self.parse_text(texts, show_names)
        wordcloud = WordCloud(background_color="white").generate(total_words)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig('photos/today.png')
        if for_users:
            query = ("SELECT DISTINCT AUTHOR, NAME FROM MESSAGES LEFT JOIN USERS ON USERS.UID=MESSAGES.AUTHOR WHERE TIMESTAMP > %s AND TIMESTAMP < %s AND NAME IS NOT NULL")
            cur.execute(query, (date_start, date_now))
            users = cur.fetchall() 
            for user in users:
               print("Starting " + user[1])
               query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND AUTHOR=%s AND TIMESTAMP > %s AND TIMESTAMP < %s")
               cur.execute(query, (user[0], date_start, date_now))
               texts = cur.fetchall()
               total_words = self.parse_text(texts, show_names)
               if len(total_words) > 5:
                   wordcloud = WordCloud(background_color="white").generate(total_words)
                   plt.imshow(wordcloud, interpolation='bilinear')
                   plt.axis("off")
                   plt.savefig('photos/' + user[1] + '.png')
        plt.cla()
    def parse_text(self, tuple_of_text, show_names):
       string_to_trim = ""
       for text in tuple_of_text:
          if len(text[0]) < 100:
             string_to_trim = " ".join([string_to_trim,text[0].lower()]) 
       string_to_trim = re.sub(r"https\S+", "", string_to_trim)
       dumb_words = open("dumbwords.txt", "r") 
       names = open('names.txt', "r")
       for dumb_word in dumb_words:
           dumb_words_stripped = (dumb_word.rstrip()).lower()
           string_to_trim = string_to_trim.replace(" "+dumb_words_stripped+" ", " ")
           string_to_trim = string_to_trim.replace("Yeah ", "")
       if not show_names:
           for name in names:
               orig_string = string_to_trim
               name_stripped = (name.rstrip()).lower()
               string_to_trim = string_to_trim.replace(" "+name_stripped+" ", " ")
               string_to_trim = string_to_trim.replace("@"+name_stripped+" ", " ")
       dumb_words.close() 
       names.close()
       return string_to_trim
    def graph_of_messages(self, timespan='week'):
        date_start, date_now = self.get_dates(timespan)
        query = ("SELECT DISTINCT AUTHOR,NAME,COUNT(DISTINCT MESSAGES.UID) FROM MESSAGES LEFT JOIN USERS ON AUTHOR=USERS.UID WHERE TIMESTAMP >%s AND TIMESTAMP<%s AND NAME IS NOT NULL GROUP BY AUTHOR,NAME ORDER  BY COUNT(DISTINCT MESSAGES.UID) DESC  LIMIT 10")
        cur.execute(query, (date_start, date_now))
        users = cur.fetchall()
        print(users)
        user_frequency={}
        for user in users:
            print("User: " + user[1])
            hour_start = date_start
            hour_end = date_start + 3600
            user_plots=[0]
            user_tweets = 0
            query = ("SELECT MESSAGES.AUTHOR,COUNT(DISTINCT MESSAGES.UID) FROM MESSAGES LEFT JOIN USERS ON AUTHOR=USERS.UID WHERE MESSAGES.AUTHOR=%s AND TIMESTAMP>%s AND TIMESTAMP < %s GROUP BY MESSAGES.AUTHOR")
            while hour_end <=date_now:
                cur.execute(query, (user[0], hour_start, hour_end))
                tweets_in_hour = cur.fetchone() 
                if not tweets_in_hour:
                    user_tweets += 0 
                else:
                    user_tweets +=  tweets_in_hour[1]
                user_plots.append(user_tweets)
                hour_start += 3600
                hour_end   += 3600
            user_frequency[user[1]] = user_plots
        for user, amount in user_frequency.items():
            plt.plot(amount, label=user)
        plt.legend(loc="best")
        plt.xlabel("Time of Day(24 Hour Clock)")
        plt.xticks(range(0,25), fontsize=5)
        plt.gca().xaxis.grid(True)
        plt.xlim(left=0.0, right=24)
        plt.ylim(bottom=0.0)
        plt.savefig("photos/messenger_frequency.png")
        plt.cla()
    def flesch(self, timespan=""):
        date_start, date_now = self.get_dates(timespan)
        query = ("SELECT DISTINCT AUTHOR, NAME FROM MESSAGES LEFT JOIN USERS ON USERS.UID=MESSAGES.AUTHOR WHERE TIMESTAMP > %s AND NAME IS NOT NULL")
        cur.execute(query, (date_start,))
        users = cur.fetchall()
        top_flescher =["duh", "-9.9"]
        for user in users:
           query = ("SELECT TEXT FROM MESSAGES WHERE ATTACHMENT_ID IS NULL AND TEXT IS NOT NULL AND AUTHOR=%s AND TIMESTAMP > %s AND TIMESTAMP < %s")
           cur.execute(query, (user[0], date_start, date_now ))
           texts = cur.fetchall()
           total_flesch = num_tuples = links_sent = average_flesch = 0
           for text in texts:
               trimmed_text = re.sub(r"http\S+", "", text[0])
               trimmed_text = re.sub(r"https\S+", "", trimmed_text)
               if trimmed_text != text[0]:
                   links_sent += 1
               if trimmed_text !="":
                   total_flesch = total_flesch + textstat.flesch_kincaid_grade(trimmed_text)
                   num_tuples += 1
           if num_tuples > 10:
               average_flesch = total_flesch / num_tuples
               if average_flesch > float(top_flescher[1]):
                   top_flescher = [user[1], str(average_flesch)]
               print(user[1] +"'s Flesch is " + str(average_flesch) + " with " + str(links_sent) + " links sent!")
        return top_flescher
    def get_dates(self, timespan = ''):
        date_start = 0
        p = '%Y-%m-%d %H:%M:%S'
        current_time = datetime.today().replace(microsecond=0)
        date_now = int(t.mktime(t.strptime(str(current_time), p)))
        if timespan == 'hour':
            last_midnight_datetime = str(current_time - timedelta(hours=1))
        elif timespan == 'day':
            last_midnight_datetime = str(current_time - timedelta(days=1))
        elif timespan =='week':
            last_midnight_datetime = str(current_time - timedelta(weeks=1))
        elif timespan =='month':
            last_midnight_datetime = str(current_time - timedelta(weeks=4))
        else:
            return 0, date_now
        current_time = str(current_time)
        date_start = int(t.mktime(t.strptime(last_midnight_datetime, p)))
        return date_start, date_now
