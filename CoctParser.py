from datetime import datetime
import yaml
import urllib.request
import pandas as pd
import pytz

def main():
    f = urllib.request.urlopen("https://raw.githubusercontent.com/beyarkay/eskom-calendar/main/manually_specified.yaml")
    content = f.read()
    f.close
    yml = yaml.safe_load(content)
    
    now = datetime.now()
    
    for change in yml['changes']:
        coct = False
        for k, v in change.items():
            if 'include' in k and 'coct' in v:
                coct = True
        if coct:
            if change['start'] < now and change['finsh'] > now:
                currentstage = change['stage']
                print(f"Current stage {currentstage}")
 
    utc = pytz.timezone('Africa/Johannesburg')
    nowutc = utc.localize(now)

    url = "https://github.com/beyarkay/eskom-calendar/releases/download/latest/machine_friendly.csv"
    df = pd.read_csv(url, parse_dates=['start', 'finsh'])
    coct1 = df[df['area_name'].str.endswith('city-of-cape-town-area-1')]
    prevstart = nowutc
    current = "None"
    nextslot = "None"
    upcoming = ""

    for i in range(coct1.index.size):
        instance = coct1.iloc[i-1]
        start = instance["start"]
        finsh = instance["finsh"]
        stage = instance["stage"]

        if nowutc > start and nowutc < finsh:
            current = f"In loadshedding From {start} to {finsh} stage {stage}"
        if prevstart <= nowutc and start > nowutc:
            nextslot = f"Next loadshedding From {start} to {finsh} stage {stage}"
        if start > nowutc and prevstart > nowutc:
            upcoming += f"Upcoming loadshedding From {start} to {finsh} stage {stage}\n"
        prevstart = start

    attrs = {
            "attributes": {"current": current,
            "next": nextslot,
            "upcoming": upcoming},

        }
    data = {
        "data": {"stage": currentstage},
        "attributes": attrs["attributes"],

    }
    print(data)
    print(data["data"])
    print(data["attributes"])
main()