#!/bin/bash

# https://askubuntu.com/questions/193737/how-to-listen-radio-from-terminal/193753

URL=$(grep -m 1 --null http "$1" |sed s/^.*http/http/ |tr -d '\r')
echo "Play mpg123 $URL"
#mplayer -prefer-ipv4 "$URL"
/usr/bin/mpg123 "$URL"
