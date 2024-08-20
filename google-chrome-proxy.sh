#!/bin/sh

urxvt -e mitmdump -s /home/gamer/bin/vimeo-capture-mitmproxyaddon.py --set termlog_verbosity=info --set=flow_detail=0 &
google-chrome-stable --proxy-server="http://127.0.0.1:8080" &
