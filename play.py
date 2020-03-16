#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##/usr/bin/env python

import json, cgi, cgitb, os, sys, subprocess, re, datetime

# Каталог с плейлистами
playlist_dir = "data"

# Для парсера m3u
class track():
    def __init__(self, length, title, path):
        self.length = length
        self.title = title
        self.path = path

# Парсер m3u плейлиста
def parseM3u(infile):
    # https://github.com/dvndrsn/M3uParser/blob/master/m3uparser.py
    """
        song info lines are formatted like:
        EXTINF:419,Alice In Chains - Rotten Apple
        length (seconds)
        Song title
        file name - relative or absolute path of file
        ..\Minus The Bear - Planet of Ice\Minus The Bear_Planet of Ice_01_Burying Luck.mp3
    """

    try:
        assert(type(infile) == '_io.TextIOWrapper')
    except AssertionError:
        infile = open(infile,'r')

    """
        All M3U files start with #EXTM3U.
        If the first line doesn't start with this, we're either
        not working with an M3U or the file we got is corrupted.
    """

    line = infile.readline()
    if not line.startswith('#EXTM3U'):
       return

    # initialize playlist variables before reading file
    playlist=[]
    song=track(None, None, None)

    for line in infile:
        line=line.strip()
        if line.startswith('#EXTINF:'):
            # pull length and title from #EXTINF line
            length,title=line.split('#EXTINF:')[1].split(',',1)
            song=track(length, title, None)
        elif (len(line) != 0):
            # pull song path from all other, non-blank lines
            song.path=line
            playlist.append(song)
            # reset the song variable so it doesn't use the same EXTINF more than once
            song=track(None, None, None)

    infile.close()
    return playlist

# Определение amixer_control воспроизведения - pvolume pswitch pswitch-joined
def get_amixer_control():
    # OrangePiZero: "'Line Out'"  Raspberry: "'master'"
    control = "master"
    out = subprocess.check_output("amixer | grep -B1 pvolume | grep -B1 pswitch | grep -v cswitch | grep -B1 Capabilities | grep 'Simple mixer control'", shell=True)
    # print("out: " + str(out))
    if out is None:
        print("ERROR get amixer out")
        return control
    re1 = []
    re1 = re.findall("\'.*\'", str(out))
    if re1[0] is None:
        print("ERROR parse amixer out")
        return control
    control = str(re1[0])
    # print("control: " + control)
    return control

def log(msg, toconsole):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open("/var/log/webuipi/webuipi.log", "a+")
    f.write(date_str + "  " + msg + "\n")
    f.close()
    if toconsole:
        print(msg)

def testpost(post, debug):
    log("testpost():", debug)
    resp = {}
    resp[0] = "got test POST request:"
    resp[1] = post
    log(json.dumps(resp), debug)
    return

def test(debug):
    log("test():", debug)
    print("Content-type: text/html\r\n\r\n")
    print("<html><head><title>Test CGI Script</title></head><body><h3> Test CGI Script </h3></body>")
    return
    
def play(playlist, debug):
    log("play(): " + playlist, debug)
    # subprocess.call(["/usr/bin/mpg123", "\"data/music/bARTek - Walking K feat. Ashes and Dreams.mp3\""])
    # subprocess.call(["/usr/bin/mpg123", "data/music/bARTek - Walking K feat. Ashes and Dreams.mp3"])
    # os.system("/usr/bin/mpg123 \"data/music/bARTek - Walking K feat. Ashes and Dreams.mp3\"")
    # subprocess.Popen(["/usr/bin/mpg123", song])
    # song = "data/music/bARTek - Walking K feat. Ashes and Dreams.mp3"
    os.system("killall mpg123 &>/dev/null ; sleep 1")

    playlist_path = playlist_dir + "/" + playlist

    if not os.path.isfile(playlist_path):
        log("ERROR: file not found: " + playlist_path, True)
        return
    if os.path.splitext(playlist_path)[1] != ".m3u":
        log("ERROR: file not m3u playlist: " + playlist_path, True)
        return

    playlist_parsed = parseM3u(playlist_path)
    song = track(None, None, None)
    for pls_track in playlist_parsed:
        log((pls_track.title + ", " + pls_track.length + ", " + pls_track.path), True)
        song = pls_track
        break

    if song.path is None:
        log("ERROR: track parse error", True)
        return

    log("Play: " + song.path, debug)
    command = ['/usr/bin/mpg123', 'mpg123', song.path]
    os.spawnlp(os.P_NOWAIT, *command)

    log("OK", True)
    exit
    return

def stop(debug):
    log("stop():", debug)
    os.system("killall mpg123 2>/dev/null")
    log("OK", True)
    return

def volume(action, debug):
    log("volume(): " + action, debug)
    # vol_str = os.system("amixer sget Master | grep \": Playback\" | grep -v Limits | grep -v grep")
    # devnull = open(os.devnull, 'wb')
    # out = subprocess.Popen(['amixer', 'sget', 'Master'], shell=False, 
    #     stdout=subprocess.PIPE, stderr=devnull)

    amixer_control = get_amixer_control()

    out = subprocess.check_output(["amixer", "sget", amixer_control])
    # stdout, stderr = out.communicate()
    if out is None:
        log("ERROR get amixer out", True)
        return
    #print("out: " + str(out))
    re1 = []
    re1 = re.findall("\[.*\%\]", str(out))
    # print "re.findall: " + "".join(re1)
    if re1.count == 0:
        log("ERROR find re1", True)
        return        
    re2 = []
    # print "re1[0]: " + str(re1[0])
    re2 = re.findall("\d+", str(re1[0]))
    # print "re2:" + "".join(re2)
    if re2.count == 0:
        log("ERROR find re2", True)
        return
    vol_str = str(re2[0])
    #print "vol_str:" + vol_str
    if not vol_str:
        log("ERROR find vol_str", True)
        return
    volume = int(vol_str)
    if action.upper() != "GET":
        if action.upper() == "UP" and volume < 96:
            volume += 5
        if action.upper() == "DOWN" and volume > 4:
            volume -= 5
        #print "/usr/bin/amixer set " + amixer_control + " \"" + str(volume) + "%\" > /dev/null"
        os.system("/usr/bin/amixer set " + amixer_control + " \"" + str(volume) + "%\" > /dev/null")
        # out = subprocess.check_output(["/usr/bin/amixer", "set", "'Master'", "\"" + str(volume) + "%\""])
        #print "out: " + out
    log(str(volume), True)
    return 

def get_playlist(debug):
    log("get_playlist():", debug)
    pls_files_list = []
    resp = {}
    for filename in os.listdir(playlist_dir):
        if filename.endswith(".m3u"):
            pls_files_list.append(filename)
        continue
    pls_files_list.sort()
    i = 0
    for pls_file in pls_files_list:
        i += 1
        resp[i] = pls_file
    log(json.dumps(resp), True)
    return

def main(argv):
    # Использование из cli: play.py volume=up
    if len(argv) > 0:
        log(str(len(sys.argv)) + " argv: " + str(argv), True)
        for arg in argv:
            print("arg: ", arg)
        args = argv[0].split("=")
        # for arg in args:
        #     print("arg: ", arg)                  
        if args[0] == "testpost":
            post = None
            if len(args) > 1:
                post = args[1]
            testpost(post, True)
            return
        if args[0] == "test":
            test(True)
            return
        if args[0] == "play":
            playlist = None
            if len(args) > 1:
                playlist = args[1]
            play(playlist, True)
            return
        if args[0] == "stop":
            stop(True)
            return
        if args[0] == "volume":
            action = ""
            if len(args) > 1:
                action = args[1].upper()
            volume(action, True)
            return
        if args[0] == "pls" or args[0] == "get":
            get_playlist(True)
            return
    else:
        req = cgi.FieldStorage()
        # resp = {}

        try:
            if req.getvalue("testpost") is not None:
                post = req.getvalue("test")
                testpost(post, None)
                return
            if req.getvalue("test") is not None:
                test(None)
                return
            # Play
            if req.getvalue("play") is not None:
                playlist = req.getvalue("play")
                play(playlist, None)
                return
            # Stop
            if req.getvalue("stop") is not None:
                stop(None)
                return
            # Volume
            if req.getvalue("volume") is not None:
                action = "GET"
                if req.getvalue("volume").upper() == "UP":
                    action = "UP"
                if req.getvalue("volume").upper() == "DOWN":
                    action = "DOWN"
                volume(action, None)
                return

            # Обработка GET-запроса, возвращает список плейлистов pls в playlist_dir
            # resp[0] = "process GET request, requset keys count: " + str(len(req.keys()))
            if (len(req.keys())) == 0:
                get_playlist(None)
                # print('{"1": "Chroma Piano.m3u", "2": "RadioC.m3u"}')
        except:
            # err = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + 
            log("Unexpected error:" + sys.exc_info()[0])


if __name__ == '__main__':
    main(sys.argv[1:])
