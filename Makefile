# - coding: utf-8 -

# Copyright (C) 2009 Sachin Patil <sachin6870 at gmail.com>

# This file is part of CricScore applet

# CricScore applet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# CricScore applet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Cric Score applet.  If not, see <http://www.gnu.org/licenses/>.

INSTALL = /usr/bin/install
MKDIR = mkdir -p
RM = rm -rf
BIN_DIR = /usr/local/bin
PIXMAPS_DIR = /usr/share/pixmaps
SERVERS_DIR = /usr/lib/bonobo/servers
DATA_DIR = /usr/share/cricscore-applet


install:
	${MKDIR} ${DATA_DIR}
	${INSTALL} -p src/cricketscore.py ${BIN_DIR}
	${INSTALL} -p src/cricscore_prefs.py ${BIN_DIR}
	${INSTALL} -p src/gnome_cricscore_globals.py ${BIN_DIR}
	${INSTALL} -p server/cricketscore.server ${SERVERS_DIR}
	${INSTALL} -p images/cricscore.png ${PIXMAPS_DIR}
	${INSTALL} -p data/GNOME_CricScoreApplet.xml ${DATA_DIR}

uninstall:
		${RM} ${DATA_DIR}
		${RM} ${BIN_DIR}/cricketscore.py
		${RM} ${BIN_DIR}/cricscore_prefs.py
		${RM} ${BIN_DIR}/gnome_cricscore_globals.py
		${RM} ${SERVERS_DIR}/cricketscore.server
		${RM} ${PIXMAPS_DIR}/cricscore.png
		${RM} ${DATA_DIR}/GNOME_CricScoreApplet.xml
