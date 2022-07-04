from datetime import datetime
import os
import time
from html.parser import HTMLParser
import urllib.request
import re
import json
import platform

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

class LoadSheddingParser(HTMLParser):
    isLoadsheddingMsg = False
    isLoadsheddingP = False
    fullMsg = ""
    def handle_starttag(self, tag, attrs):
        if (tag == 'div'):
            for key,value in attrs:
                if (key == 'class' and value=='alertBody'):
                    self.isLoadsheddingMsg = True
        if (self.isLoadsheddingMsg == True and tag == 'p'):
            self.isLoadsheddingP = True

    def handle_data(self, data):
        if (self.isLoadsheddingP):
            #print("Data     :", data)
            self.fullMsg += data

    def handle_endtag(self, tag):
        if (self.isLoadsheddingP and tag == 'p'):
            self.isLoadsheddingP = False
        if (self.isLoadsheddingMsg and tag == 'div'):
            self.isLoadsheddingMsg = False

os.environ['TZ'] = 'Africa/Johannesburg'
if (not platform.system() == 'Windows'):
    time.tzset()
date = datetime.now()
currentTime = date.time()
hour = currentTime.hour

try:
    with open("loadshedding.json", "r") as json_file:
        if (json_file):
            loadshedding_data = json.load(json_file)
            lastdate = datetime.fromisoformat(loadshedding_data['timestamp'])
            difference = date - lastdate
            if (difference.seconds / 60 < 5):
                print("Stage ", loadshedding_data['stage'])
                exit(0)
except FileNotFoundError:
    currentStage = -1

page = urllib.request.urlopen("https://www.capetown.gov.za/")
content = page.read()
parser = LoadSheddingParser()
parser.feed(content.decode("utf-8"))

currentStage = 0

message = re.findall("City customers on Stage (\d) from (\d{2}):00 -.(\d{2}):00, then.Stage (\d) from (\d{2}):00 - (\d{2}):00 on (\w+)", parser.fullMsg)

if (message):
    matches = message[0]

    schedule = {
        'stage': int(message[0][0]),
        'from': currentTime.hour,
        'to': int(message[0][1])
    }
    schedules = [schedule]

    schedule = {
        'stage': int(message[0][3]),
        'from': int(message[0][4]),
        'to': int(message[0][5])
    }
    schedules = [schedule]

if (not message):
    message = re.findall("City customers on Stage (\d) from (\d{2}):00 -.(\d{2}):00", parser.fullMsg)

    if (message):
        schedule = {
            'stage': int(message[0][0]),
            'from': currentTime.hour,
            'to': int(message[0][1])
        }
        schedules = [schedule]

if (not message):
    message = re.findall("City customers on Stage (\d) until.(\d{2}):00 on Sunday, then Stage (\d) from (\d{2}):00 until.(\d{2}):00", parser.fullMsg)

    if (message):
        schedule = {
            'stage': int(message[0][0]),
            'from': currentTime.hour,
            'to': int(message[0][1])
        }
        schedules = [schedule]

        schedule = {
            'stage': int(message[0][2]),
            'from': int(message[0][1]),
            'to': int(message[0][3])
        }

        schedules.append(schedule)

if (not message):
    message = re.findall("City customers on Stage (\d) until.(\d{2}):00, then Stage (\d) until (\d{2}):00..Stage (\d) from (\d{2}):00 - (\d{2}):00 and Stage (\d) from (\d{2}):00 - (\d{2}):00 on Monday..Check the schedule and be prepared for outages.", parser.fullMsg)

    if (message):
        schedule = {
            'stage': int(message[0][0]),
            'from': currentTime.hour,
            'to': int(message[0][1])
        }
        schedules = [schedule]

        schedule = {
            'stage': int(message[0][2]),
            'from': int(message[0][1]),
            'to': int(message[0][3])
        }

        schedules.append(schedule)

        schedule = {
            'stage': int(message[0][4]),
            'from': int(message[0][5]),
            'to': int(message[0][6])
        }

        schedules.append(schedule)

        schedule = {
            'stage': int(message[0][7]),
            'from': int(message[0][8]),
            'to': int(message[0][9])
        }

        schedules.append(schedule)

if (not message):
    message = re.findall("City customers: Stage (\d) underway until (\d{2}):00", parser.fullMsg)

    if (message):
        schedule = {
            'stage': int(message[0][0]),
            'from': currentTime.hour,
            'to': int(message[0][1])
        }
        schedules = [schedule]

for item in schedules:
    fromhour = item['from']
    tohour = item['to']
    if (fromhour < tohour):
        if (hour >= fromhour and hour < tohour):
            currentStage = item['stage']
            break
    if (fromhour > tohour):
        if ((hour >= fromhour and hour <= 23 ) or (hour >= 0 and hour < tohour)):
            currentStage = item['stage']
            break

print("Stage ", currentStage)

loadshedding_data = {
    'stage': currentStage,
    'timestamp': date
}

with open('loadshedding.json', 'w') as json_file:
    json.dump(loadshedding_data, cls=DateTimeEncoder, fp=json_file)
