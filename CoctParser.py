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
                print(change['stage'])
 
    utc = pytz.timezone('Africa/Johannesburg')
    nowutc = utc.localize(now)

    url = "https://github.com/beyarkay/eskom-calendar/releases/download/latest/machine_friendly.csv"
    df = pd.read_csv(url, parse_dates=['start', 'finsh'])
    coct1 = df[df['area_name'].str.endswith('city-of-cape-town-area-1')]
    prevstart = nowutc
    for i in range(coct1.index.size-1):
        instance = coct1.iloc[i]
        start = instance["start"]
        finsh = instance["finsh"]
        stage = instance["stage"]

        if nowutc > start and nowutc < finsh:
            print(f"In loadshedding From {start} to {finsh} stage {stage}")
        if prevstart < nowutc and start > nowutc:
            print(f"Next loadshedding From {start} to {finsh} stage {stage}")
        if start > nowutc and prevstart > nowutc:
            print(f"Upcoming loadshedding From {start} to {finsh} stage {stage}")
        prevstart = start
main()