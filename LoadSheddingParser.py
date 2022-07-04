from datetime import datetime
import os
import time
from html.parser import HTMLParser
import urllib.request
import re
import json
import platform

#emit datetime in iso format
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

#parse the html and extract the loadshedding alert message
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
            self.fullMsg += data

    def handle_endtag(self, tag):
        if (self.isLoadsheddingP and tag == 'p'):
            self.isLoadsheddingP = False
        if (self.isLoadsheddingMsg and tag == 'div'):
            self.isLoadsheddingMsg = False


def getCurrentTime():
    os.environ['TZ'] = 'Africa/Johannesburg'
    if (not platform.system() == 'Windows'):
        time.tzset()
    return datetime.now()

def getCachedStage(currentDate):
    try:
        with open("loadshedding.json", "r") as json_file:
            if (json_file):
                loadshedding_data = json.load(json_file)
                lastdate = datetime.fromisoformat(loadshedding_data['timestamp'])
                difference = currentDate - lastdate
                if (difference.seconds / 60 < 5):
                    return loadshedding_data['stage']
                    exit(0)
                return -1
    except FileNotFoundError:
        return -1

def getMessage():
    page = urllib.request.urlopen("https://www.capetown.gov.za/")
    content = page.read()
    parser = LoadSheddingParser()
    parser.feed(content.decode("utf-8"))
    return parser.fullMsg

def determineStage(fullMsg, currentHour, weekday):
    weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    message = re.findall("City customers on Stage (\d) from (\d{2}):00 -.(\d{2}):00, then.Stage (\d) from (\d{2}):00 - (\d{2}):00 on (\w+)", 
                    fullMsg)
    currentStage = 0
    if (message):
        matches = message[0]

        schedule = {
            'stage': int(message[0][0]),
            'from': currentHour,
            'to': int(message[0][1])
        }
        schedules = [schedule]

        schedule = {
            'stage': int(message[0][3]),
            'from': int(message[0][4]),
            'to': int(message[0][5]),
            'weekDay': message[0][6]
        }
        schedules = [schedule]

    if (not message):
        message = re.findall("City customers on Stage (\d) from (\d{2}):00 -.(\d{2}):00", 
                    fullMsg)

        if (message):
            schedule = {
                'stage': int(message[0][0]),
                'from': currentHour,
                'to': int(message[0][1])
            }
            schedules = [schedule]

    if (not message):
        message = re.findall("City customers on Stage (\d) until.(\d{2}):00 on (\w+), then Stage (\d) from (\d{2}):00 until.(\d{2}):00", 
                            fullMsg)

        if (message):
            schedule = {
                'stage': int(message[0][0]),
                'from': currentHour,
                'to': int(message[0][1])
            }
            schedules = [schedule]

            schedule = {
                'stage': int(message[0][3]),
                'from': int(message[0][1]),
                'to': int(message[0][4])
            }

            schedules.append(schedule)

    if (not message):
        message = re.findall("City customers on Stage (\d) until.(\d{2}):00, then Stage (\d) until (\d{2}):00..Stage (\d) from (\d{2}):00 - (\d{2}):00 and Stage (\d) from (\d{2}):00 - (\d{2}):00 on (\w+)", 
                            fullMsg)

        if (message):
            schedule = {
                'stage': int(message[0][0]),
                'from': currentHour,
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
                'to': int(message[0][9]),
                'weekDay': message[0][10]
            }

            schedules.append(schedule)

    if (not message):
        #City customers: Stage 4 underway until 00:00, Stage 2: from 00:00 until 05:00 on Tuesday
        message=re.findall("City customers: Stage (\d) underway until (\d{2}):00, Stage (\d).*from (\d{2}):00 until.(\d{2}):00 on (\w+)", fullMsg)

        if (message):
            schedule = {
                'stage': int(message[0][0]),
                'from': currentHour,
                'to': int(message[0][1]),
                'weekDay': weekDays[weekDays.index(message[0][5])-1]
            }
            schedules = [schedule]

            schedule = {
                'stage': int(message[0][2]),
                'from': int(message[0][3]),
                'to': int(message[0][4]),
                'weekDay': message[0][5]
            }
            schedules.append(schedule)

    if (not message):
        #City customers: Stage 4 underway until 00:00
        message = re.findall("City customers: Stage (\d) underway until (\d{2}):00", 
                        fullMsg)

        if (message):
            schedule = {
                'stage': int(message[0][0]),
                'from': currentHour,
                'to': int(message[0][1])
            }
            schedules = [schedule]

    for item in schedules:
        fromhour = item['from']
        tohour = item['to']
        if (fromhour < tohour):
            if (currentHour >= fromhour and currentHour < tohour and weekday == weekDays.item(item['weekDay'])):
                currentStage = item['stage']
                break
        if (fromhour > tohour):
            if (((currentHour >= fromhour and currentHour <= 23 ) or (currentHour >= 0 and currentHour < tohour)) and weekday == weekDays.index(item['weekDay'])):
                currentStage = item['stage']
                break
    return currentStage

def main():
    currentTime = getCurrentTime()
    currentStage = getCachedStage(currentTime)

    if (currentStage == -1):
        messsage = getMessage()

        currentStage = determineStage(messsage, currentTime.time().hour, currentTime.weekday())

    loadshedding_data = {
        'stage': currentStage,
        'timestamp': currentTime
    }

    with open('loadshedding.json', 'w') as json_file:
        json.dump(loadshedding_data, cls=DateTimeEncoder, fp=json_file)

    return currentStage
