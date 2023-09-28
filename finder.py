import wexpect #python's more standard - subprocces - fails to capture stdout?
import os
import re
import urllib.request
import csv
import json
import datetime
import sys


delete = False
def main():
    fen = input("paste fen code")
   #test: fen =  "8/8/p1k1r3/1p6/1P5R/8/2K5/8 w - - 13 70\n"
    try:
        p = wexpect.spawn('cmd') 
        p.expect('>')

        test =send(p,'"C:\\Scid vs PC\\bin\\tcscid.exe"\n')
        if(test[0]==1): #still on cmd prompt
            print("invalid scid location!")
            return
        

        for file in os.listdir("games"):
            if(file.endswith(".pgn")):
                search(p, fen, file)

        read(p, fen) #get more games from csv file
        p.sendline('exit')
        p.terminate()
    except KeyboardInterrupt:
        p.sendline('exit')
        p.terminate()
        sys.exit(0)

def send(p, command):
    p.sendline(command)
    test = p.expect(['%', '>'])
    output=p.before[len(command):]
    output=output.strip()
    return(test, output)

def search(p, pos, games):
    print(f'searchin position from {games}' + ' '*100, end='\r') #"progress bar", overwrites ending with spaces
    
    test =send(p,'sc_base create myfile\n') #output: test[1]=='1', no reason to expect failure here :)
    #myfile is random name for base

    test = send(p, f'sc_base import file "games/{games}"\n')
    if not (test[1][:1] in '123456789'):
       #print(f'err:  {test[1]}') # invalid command, filename or  just zero games(probably wrong file extention) # but no reason to print, as api can return empty files
       return
    
    test = send(p, f'sc_game startBoard "{pos}"\n')
    if(test[1]): #no errors means empty output
        print("wrong fen")
        return
    
    send(p, 'sc_search board 2 E true false\n') # no error check neccessary any more
# but if data is needed:
    #pattern = r"(\d+)\s/\s(\d+)\s\s\((\d+\.\d+) s\)"  - 
    #match = re.search(pattern, test[1])
    #x = int(match.group(1))
    #y = int(match.group(2))
    #time = float(match.group(3))
    test = send(p, 'sc_filter first\n')
    id = int(test[1])
    while (id>0):
        send(p, f'sc_game load {id}\n')
        game =send(p, 'sc_game pgn -comments 0')# cant read comments as clocktime %emt uses default prompt symbol
        print(game[1])

        test = send(p, 'sc_filter next\n')
        id = int(test[1])
    
    send(p, 'sc_base close')
    if(delete):
        os.remove(f'games/{games}')


def limits():
    timerange= input("Limit search query with time range (YYYY/MM YYYY/MM)")
    times = timerange.split()
    pattern = r"(\d{4})(?:/(\d{2}))?"
    if not(times):#empty input
        return False
    match = re.match(pattern, times[0])
    if(match):
        month = match.group(2)
        if(month is None):
            times[0] = times[0] +"/01"
    else:
        return False
    if(len(times)==2):
        match = re.match(pattern, times[1])
        if(match):
            month = match.group(2)
            if(month is None):
                times[1] = times[1] +"/12"
        else:
            return False
    else:
        times.append("tmp")
        times[1] = times[0]
        times[1] = times[1].replace("/01", "/12") #year end
    return(times)

def read(p, pos): #get more games from chesscom api
    timerange = limits()
    if(timerange):
        mindate = timerange[0]
        maxdate = timerange[1]
    
    else:
        current_date = datetime.date.today()
        maxdate =current_date.strftime("%Y/%m")
        mindate = '2007/07' #first game ever recorded on site?

    base = 'https://api.chess.com/pub/player/'
    archive = '/games/archives'
    with open('names.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header=True
        for line in csv_reader:
            if(header): #first row is irrelevant
                header=False
                continue
            # print(f'{line[0]} username is {line[1]} on chess.com')

            request = urllib.request.urlopen(base + line[1] + archive)

            dates = json.loads(request.read())

            for link in(dates["archives"]):
                date =link.split("/", 7)
                diff= date[7].replace('/','_')# extra '/' breaks expected path, by Content-Disposition: attachment it should be empty, but '_' makes it more readable?
                diff = '_' + diff
                filename = 'games/ChessCom_' + line[1] + diff+ '.pgn'
                
                if(mindate <= date[7] <= maxdate):
                    print('downloading: ', filename)
                    urllib.request.urlretrieve(link + '/pgn', filename)
                    search(p, pos, filename)


if __name__ == "__main__":
    main()
