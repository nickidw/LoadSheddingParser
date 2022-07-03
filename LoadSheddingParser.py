from datetime import datetime
from html.parser import HTMLParser
import urllib.request
import re
import json

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


date = datetime.now()
time = date.time()
hour = time.hour

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

    stage = int(matches[0])
    stagefrom = int(matches[1])
    stageto=int(matches[2])

    if (len(matches) == 7):
        stagenext=int(matches[3])
        stagenextfrom=int(matches[4])
        stagenextto=int(matches[5])
        stagenextday=matches[6]

    if (stagefrom < stageto):
        if (hour >= stagefrom and hour < stageto):
            currentStage = stage

    if (stagenextfrom > stagenextto):
        if (hour >= stagenextfrom or hour < stagenextto):
            currentStage = stagenext

if (currentStage == 0):
    message = re.findall("City customers on Stage (\d) from (\d{2}):00 -.(\d{2}):00", parser.fullMsg)

    if (message):
        matches = message[0]

        stage = int(matches[0])
        stagefrom = int(matches[1])
        stageto=int(matches[2])

        if (stagefrom < stageto):
            if (hour >= stagefrom and hour < stageto):
                currentStage = stage

if (currentStage == 0):
    message = re.findall("City customers on Stage (\d) until.(\d{2}):00 on Sunday, then Stage (\d) from (\d{2}):00 until.(\d{2}):00", parser.fullMsg)

    if (message):
        matches = message[0]

        stage = int(matches[0])
        stageto = int(matches[1])
        stagenext = int(matches[2])
        stagenextfrom = int(matches[3])
        stagenextto = int(matches[4])

        if (hour < stageto):
            currentStage = stage

        if (stagenextfrom < stagenextto):
            if (hour >= stagenextfrom and hour < stagenextto):
                currentStage = stagenext

print("Stage ", currentStage)

loadshedding_data = {
    'stage': currentStage,
    'timestamp': date
}

with open('loadshedding.json', 'w') as json_file:
    json.dump(loadshedding_data, cls=DateTimeEncoder, fp=json_file)
