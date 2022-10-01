from datetime import datetime
import yaml
import urllib.request

def main():
    print("hello")
    f = urllib.request.urlopen("https://raw.githubusercontent.com/beyarkay/eskom-calendar/main/manually_specified.yaml")
    content = f.read()
    yml = yaml.safe_load(content)
    
    for change in yml['changes']:
        coct = False
        for k, v in change.items():
            if 'include' in k and 'coct' in v:
                coct = True
        if coct:
            now = datetime.now()
            if change['start'] < now and change['finsh'] > now:
                print(change['stage'])
    #print(yml)

main()