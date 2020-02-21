import json, time
from datetime import datetime

t1 = datetime.timestamp(datetime.now())
time.sleep(2.0)
t2 = datetime.timestamp(datetime.now())

li = [
    {'Username': 'Pepe', 'Message': 'Hola', 'Timestamp': t2},
    {'Username': 'Juan', 'Message': 'adios', 'Timestamp': t1}
    ]
newest_msg = sorted(li, key=lambda k: k['Timestamp'])
print(json.dumps(newest_msg[:2]))

f = "dd/mm/yyyy hh:MM:ss"
for m in newest_msg:
    print(datetime.fromtimestamp(m['Timestamp']).strftime("%H:%M"))

print(type(1582222050320))
print(datetime.fromtimestamp(1582222050320/1000).strftime("%H:%M"))