#!/bin/sh

# Check root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Arguments
while [ "$1" != "" ]; do
    case $1 in
        -na | --noapt | --no-apt )
            NOAPT="Y"
            ;;
        -ng | --no-git-clone | --nogitclone | --nogit )
            NOGIT_CLONE="Y"
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
    aptitude -y install lighttpd alsa-utils mpg123
    # lighttpd config
    REPLACE_FROM="static-file.exclude-extensions.*"
    REPLACE_TO="static-file.exclude-extensions = ( \".php\", \".pl\", \".fcgi\", \".py\" )"
    sed -i -e "s/$REPLACE_FROM/$REPLACE_TO/g" /etc/lighttpd/lighttpd.conf
    REPLACE_FROM="server.username.*"
    REPLACE_TO="server.username             = \"pi\""
    sed -i -e "s/$REPLACE_FROM/$REPLACE_TO/g" /etc/lighttpd/lighttpd.conf
    [ -f /etc/lighttpd/conf-enabled/10-cgi.conf ] && rm -f /etc/lighttpd/conf-enabled/10-cgi.conf
    /bin/cat <<EOF >/etc/lighttpd/conf-enabled/10-cgi.conf
server.modules += ( "mod_cgi" )
\$HTTP["url"] =~ "^/cgi-bin/" { cgi.assign = ( "" => "" ) }
cgi.assign = ( ".py"  => "/usr/bin/python3", )
EOF
    echo "Restarting lighttpd"
    systemctl restart lighttpd; systemctl status lighttpd
fi

# git clone
if [ ! -n "$NOGIT_CLONE" ]; then
    GIT_STATUS=$(dpkg -l | grep "git\ ")
    if [ ! -n "$GIT_STATUS" ]; then
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
    [ -f "$HTTP_HOME/index.lighttpd.html" ] && mv "$HTTP_HOME/index.lighttpd.html" "$HTTP_HOME/../index.lighttpd.html"
    rm -rf "$HTTP_HOME/*"
    cp -R webuipi/* "$HTTP_HOME/"
    rm -rf webuipi
    [ -f "$HTTP_HOME/../index.lighttpd.html" ] && mv "$HTTP_HOME/../index.lighttpd.html" "$HTTP_HOME/index.lighttpd.html"
    cd "$C_PWD"
fi

# Permission
echo "Set permissions"
chown -R pi:www-data "$HTTP_HOME"
chown -R pi:www-data /var/run/lighttpd
chown -R pi:www-data /var/log/lighttpd
[ -d "$HTTP_HOME/data" ] && mkdir -p "$HTTP_HOME/data"
#chown -R pi:www-data "$HTTP_HOME/data"
chmod -R 775 "$HTTP_HOME/data"

echo ".Done"


