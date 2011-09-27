#!/bin/sh

cp src/cricketscore.py /usr/local/bin
cp src/cricscore_prefs.py /usr/local/bin
cp src/gnome_cricscore_globals.py /usr/local/bin
cp server/cricketscore.server /usr/lib/bonobo/servers/
cp images/cricscore.png /usr/share/pixmaps/

if [ ! -d "/usr/share/cricscore-applet" ]; then
mkdir /usr/share/cricscore-applet
fi
cp data/GNOME_CricScoreApplet.xml /usr/share/cricscore-applet
