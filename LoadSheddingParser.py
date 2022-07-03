from datetime import datetime
from html.parser import HTMLParser
import urllib.request
import re

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

page = urllib.request.urlopen("https://www.capetown.gov.za/")
content = page.read()
parser = LoadSheddingParser()
parser.feed(content.decode("utf-8"))

message = re.findall("City customers on Stage (\d) from (\d{2}):00 - (\d{2}):00, then.Stage (\d) from (\d{2}):00 - (\d{2}):00 on (\w+)", parser.fullMsg)

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

    time = datetime.now().time()
    hour = time.hour
    if (stagefrom < stageto):
        if (hour >= stagefrom and hour < stageto):
            currentStage = stage

    if (stagenextfrom > stagenextto):
        if (hour >= stagenextfrom or hour < stagenextto):
            currentStage = stagenext
else:
    message = re.findall("City customers on Stage (\d) until.(\d{2}):00 on Sunday, then Stage (\d) from (\d{2}):00 until (\d{2}):00", parser.fullMsg)

    if (message):
        matches = message[0]

        stage = int(matches[0])
        stageto = int(matches[1])
        stagenext = int(matches[2])
        stagenextfrom = int(matches[3])
        stagenextto = int(matches[4])

        time = datetime.now().time()
        hour = time.hour
        if (hour < stageto):
            currentStage = stage

        if (stagenextfrom < stagenextto):
            if (hour >= stagenextfrom and hour < stagenextto):
                currentStage = stagenext


print("Stage ", currentStage)