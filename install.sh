#!/bin/sh

# Check root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Arguments
while [ "$1" != "" ]; do
    case $1 in
        -g | -c | --git-clone | --gitclone | --git )
            GIT_CLONE="Y"
            ;;
        -n | --noapt | --no-apt )
            NOAPT="Y"
            ;;
#        -f | --file )           
#            shift
#            filename=$1
#           ;;
#        -i | --interactive )    
#            interactive=1
#            ;;
        -h | --help )
            help
            exit
            ;;
#        * )
#            help
#            exit 1
    esac
    shift
done

C_PWD=$PWD
HTTP_HOME="/var/www/html"

# git clone
if [ ! -n "$GIT_CLONE" ]; then
    GIT_STATUS=$(dpkg -l | grep "git\ ")
    if [ -n "$GIT_STATUS" ]; then
        echo "Install git package"
        apt-get update
        APT_UPDATED="Y"
        apt-get install git
    fi
    echo "Clone webuipi"
    cd /tmp
    [ -f webuipi ] && rm -f webuipi
    [ -d webuipi ] && rm -rf webuipi
    git clone https://github.com/tyrell81/webuipi.git
#    [ -f "$HTTP_HOME/webuipi" ] && rm -f "$HTTP_HOME/webuipi"
#    [ -d "$HTTP_HOME/webuipi" ] && mv "$HTTP_HOME/webuipi" "$HTTP_HOME/webuipi.bak"
    mv webuipi/* "$HTTP_HOME/"
    rmdir webuipi
    cd "$HTTP_HOME"
fi

# Install lighttpd, alsa, mpg123
#if [ ! -n "$NOAPT" ]]; then echo "noapt IS EMPTY"; else echo "NOAPT!"; fi
if [ ! -n "$NOAPT" ]; then
    echo "Install aptitude alsa-utils mpg123"
    if [ -n "$APT_UPDATED" ]; then
        apt-get update
    fi
    APTITUDE_STATUS=$(dpkg -l | grep "git\ ")
    if [ -n "$APTITUDE_STATUS" ]; then
        apt-get install aptitude
    fi
    aptitude -y install alsa-utils mpg123
    # lighttpd config
    REPLACE_FROM="static-file.exclude-extensions*"
    REPLACE_TO="static-file.exclude-extensions = ( \".php\", \".pl\", \".fcgi\", \".py\" )"
    sed -i -e "s/$REPLACE_FROM/$REPLACE_TO/g" /etc/lighttpd/lighttpd.conf
    echo "Restarting lighttpd"
    systemctl restart lighttpd; systemctl status lighttpd
fi

# Permission
echo "Set permissions"
chown -R www-data:www-data "$HTTP_HOME/*"
[ -d "$HTTP_HOME/data" ] && mkdir -p "$HTTP_HOME/data"
chown -R www-data:pi "$HTTP_HOME/data"
chmod -R 775 "$HTTP_HOME/data"

echo ".Done"


