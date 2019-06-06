sudo usermod -a -G crontab pi
sudo cp -f /home/pi/webuipi/bin/lighttpd.conf /etc/lighttpd/ && sudo systemctl restart lighttpd && sudo systemctl status lighttpd
