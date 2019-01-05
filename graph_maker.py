from datetime import datetime, time
import time as t
import psycopg2
import json
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

conf = json.load(open('creds/config.json', 'r'))

conn = psycopg2.connect("dbname=messenger user=sp1r3")
cur = conn.cursor()

cur.execute('SELECT NAME, COUNT(NAME) FROM MESSAGES RIGHT JOIN USERS ON author=uid WHERE THREADID=%s GROUP BY NAME', (conf["thread_main"],));
messagesent = cur.fetchall()
names = []
numsent = []
for msg in messagesent:
    names.append(msg[0])
    numsent.append(msg[1])
#    msgtime = t.strftime('%Y-%m-%d %H:%M:%S', t.localtime(int(ts[0])))

midnight = datetime.combine(datetime.today(), time.hour(8))

print(midnight)
fig1, ax1 = plt.subplots()
ax1.pie(numsent, labels = names, shadow=True, startangle=90)
ax1.axis('equal')
plt.show()
