#!/bin/sh
VOL="$1"
/usr/bin/amixer set 'PCM' "$VOL%"
