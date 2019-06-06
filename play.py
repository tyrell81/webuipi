#!/usr/bin/env python
import json, cgi, cgitb, os, sys, subprocess, re

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


def main(argv):
    # Каталог с плейлистами
    playlist_dir = "/home/pi/playlist"    
    req = cgi.FieldStorage()

    resp = {}

    # Test
    if req.getvalue("test") is not None:
        resp[0] = "got test POST request:"
        resp[1] = req.getvalue("test")
        print json.dumps(resp)
        return

    # Play
    if req.getvalue("play") is not None:
        # subprocess.call(["/usr/bin/mpg123", "\"/home/pi/music/bARTek - Walking K feat. Ashes and Dreams.mp3\""])
        # subprocess.call(["/usr/bin/mpg123", "/home/pi/music/bARTek - Walking K feat. Ashes and Dreams.mp3"])
        # os.system("/usr/bin/mpg123 \"/home/pi/music/bARTek - Walking K feat. Ashes and Dreams.mp3\"")
        # subprocess.Popen(["/usr/bin/mpg123", song])        
        # song = "/home/pi/music/bARTek - Walking K feat. Ashes and Dreams.mp3"        
        os.system("killall mpg123")

        playlist = req.getvalue("play")

        playlist_path = playlist_dir + "/" + playlist

        if not os.path.isfile(playlist_path):
            print "ERROR: file not found: " + playlist_path
            return
        if os.path.splitext(playlist_path)[1] != ".m3u":
            print "ERROR: file not m3u playlist: " + playlist_path
            return

        playlist_parsed = parseM3u(playlist_path)
        song = track(None, None, None)
        for pls_track in playlist_parsed:
            print (pls_track.title, pls_track.length, pls_track.path)
            song = pls_track
            break

        if song.path is None:
            print "ERROR: track parse error"
            return

        command = ['/usr/bin/mpg123', 'mpg123', song.path]
        os.spawnlp(os.P_NOWAIT, *command)
    
        print "OK"
        exit
        return

    # Stop
    if req.getvalue("stop") is not None:
        os.system("killall mpg123")
        print "OK"
        return

    # Volume get
    if req.getvalue("volume") is not None:
        # vol_str = os.system("amixer sget Master | grep \": Playback\" | grep -v Limits | grep -v grep")
        # devnull = open(os.devnull, 'wb')
        # out = subprocess.Popen(['amixer', 'sget', 'Master'], shell=False, 
        #     stdout=subprocess.PIPE, stderr=devnull)

        master = "'Master'"
        
        out = subprocess.check_output(["amixer", "sget", master])
        # stdout, stderr = out.communicate()
        if out is None:
            print "ERROR get out"
            return
        # print "out: " + out
        re1 = []
        re1 = re.findall("\[.*\%\]", str(out))
        # print "re.findall: " + "".join(re1)
        if re1.count == 0:
            print "ERROR find re1"
            return        
        re2 = []
        # print "re1[0]: " + str(re1[0])
        re2 = re.findall("\d+", str(re1[0]))
        # print "re2:" + "".join(re2)
        if re2.count == 0:
            print "ERROR find re2"
            return
        vol_str = str(re2[0])
        # print "vol_str:" + vol_str
        if not vol_str:
            print "ERROR find vol_str"
            return
        volume = int(vol_str)
        if req.getvalue("volume").upper() != "GET":
            if req.getvalue("volume").upper() == "UP" and volume < 100:
                volume += 1
            if req.getvalue("volume").upper() == "DOWN" and volume > 0:
                volume -= 1
            os.system("/usr/bin/amixer set " + master + " \"" + str(volume) + "%\" > /dev/null")
            # out = subprocess.check_output(["/usr/bin/amixer", "set", "'Master'", "\"" + str(volume) + "%\""])
            # print "out: " + out
        print str(volume)
        return 

    # Обработка GET-запроса, возвращает список плейлистов pls в playlist_dir
    # resp[0] = "process GET request, requset keys count: " + str(len(req.keys()))
    if len(req.keys()) == 0:
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
        print json.dumps(resp)        
        return

if __name__ == '__main__':
    main(sys.argv[1:])