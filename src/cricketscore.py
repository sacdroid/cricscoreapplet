#!/usr/bin/env python


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

from gettext import gettext as _
import cricscore_prefs
import gnome.ui
import gnome_cricscore_globals
import gnomeapplet
import gtk
import gtk.gdk
import gobject
import pygtk
import sys
import urllib2
import pynotify
import xml.etree.ElementTree as etree
from xml.dom import minidom
import io
import os
import logging
import string

pygtk.require('2.0')
LOG_FORMAT = "%(levelname)s [%(name)s] %(message)s"

class State:
    (NotSelected, SelectionChanged, Preview, Stump, InProgress, Lunch, Tea, Complete) = range(0, 8)

class Score(object):    
    SCORE_URL = "<this should be the URL of score file>"
    selectedMatchUrl = ""
    lastModified = ""
    state = State.NotSelected
    showScoreUpdate = True
    notificationTimeOut = 3000
    
    def __init__(self):
     self.vars = {} # dictionary variables read from the score file
    
    def refresh(self):
     logging.log(logging.DEBUG, 'refresh')
     """Refresh the score"""
     if  self.selectedMatchUrl == "":
         state = State.NotSelected
         return     
     req = urllib2.urlopen(self.selectedMatchUrl)
     lastModified = req.headers.get('last-modified') 
     logging.log(logging.DEBUG, "lastModified " +lastModified + " self.lastModified " + self.lastModified)
     if self.state != State.SelectionChanged and lastModified == self.lastModified:
        return
     self.lastModified = lastModified
     feed = req.read()
     feedStr = io.StringIO(unicode(feed));
     if feedStr == "":
        return
     xmldoc = minidom.parse(feedStr)
     match = xmldoc.getElementsByTagName('state')
     newState = match[0].firstChild.data

     if newState == 'preview':
        self.state = State.Preview
     
     if newState == 'stump':
        self.state = State.Stump
        
     if newState == 'inprogress':
        self.state = State.InProgress
     
     if newState == 'lunch':
        self.state = State.Lunch
     
     if newState == 'tea':
        self.state = State.Tea 
      
     if 'complete' in newState:
         self.state = State.Complete          
      
     logging.log(logging.DEBUG, self.state)
     if(self.state == State.Preview):
         logging.log(logging.WARNING,"Match is in preview state")
         return
     match = xmldoc.getElementsByTagName('lastwicket')
     self.vars['lastwicket'] = match[0].firstChild.data
     self.vars['lastwicketruns'] = match[0].firstChild.data
     self.vars['lastwicketnbr'] = match[0].firstChild.data
     
     match =  xmldoc.getElementsByTagName('batteamruns')
     self.vars['batteamruns'] = match[0].firstChild.data
     match =xmldoc.getElementsByTagName('batteamwkts')
     self.vars['batteamwkts'] = match[0].firstChild.data
     
     match =  xmldoc.getElementsByTagName('batteamname')
     self.vars['batteamname'] = match[0].firstChild.data
     match =xmldoc.getElementsByTagName('bwlteamname')
     self.vars['bwlteamname'] = match[0].firstChild.data
          
     match = xmldoc.getElementsByTagName('line')
     commentary = match[0].firstChild.data 
     if self.showScoreUpdate and '<b>' in commentary and self.state not in (State.Stump, State.Lunch, State.Tea):
          self.notify("{0} VS {1}".format( self.vars['batteamname'], self.vars['bwlteamname']),commentary)
     
     match =xmldoc.getElementsByTagName('batteamname')
     self.vars['batteamname'] = match[0].firstChild.data
     match =xmldoc.getElementsByTagName('batteamovers')
     self.vars['batteamovers'] = match[0].firstChild.data
     
     elements = xmldoc.getElementsByTagName('batsman')
     i = 1;
     for element in elements:
         try:
            self.vars['batsman' + str(i)] =element.getElementsByTagName('name')[0].firstChild.data
            self.vars['batsman'+ str(i) +'runs'] = element.getElementsByTagName('runs')[0].firstChild.data
            self.vars['batsman'+ str(i) +'ballsfaced'] = element.getElementsByTagName('balls-faced')[0].firstChild.data
            i = i+1
            if i == 3: break
         except:
            logging.log(logging.WARNING, "Unexpected error : %s", sys.exc_info()[0]); 
            continue
         
     elements = xmldoc.getElementsByTagName('bowler')
     i = 1;
     for element in elements:
       try:
         self.vars['bowler' + str(i)] =element.getElementsByTagName('name')[0].firstChild.data
         self.vars['bowler'+ str(i) +'overs'] = element.getElementsByTagName('overs')[0].firstChild.data
         self.vars['bowler'+ str(i) +'runs'] = element.getElementsByTagName('runs')[0].firstChild.data
         self.vars['bowler'+ str(i) +'maidens'] = element.getElementsByTagName('maidens')[0].firstChild.data
         self.vars['bowler'+ str(i) +'wickets'] = element.getElementsByTagName('wickets')[0].firstChild.data
         i = i+1
         if i == 3: break
       except :
           logging.log(logging.WARNING, "Unexpected error: %s", sys.exc_info()[0]); 
           continue
    
    def getLastWicket(self):
        return "{0} Out!! \n( {1}/{2} )".format( self.vars['lastwicket'], self.vars['lastwicketruns'], self.vars['lastwicketnbr'])
    
    def getBatTeamScore(self):
        return "{0} : {1}/{2} ({3})".format( self.vars['batteamname'], self.vars['batteamruns'], self.vars['batteamwkts'], self.vars['batteamovers'])
    
    def getTooltip(self):
        toolTip = ""
        if self.vars.has_key('batsman1') :
           toolTip = "{0} : {1}/{2}".format(self.vars['batsman1'], self.vars['batsman1runs'],  self.vars['batsman1ballsfaced'])
        if self.vars.has_key('batsman2') :
           toolTip = toolTip +   "\n{0} : {1}/{2}".format(self.vars['batsman2'], self.vars['batsman2runs'],  self.vars['batsman2ballsfaced'])
        return toolTip
    
    def getTooltip1(self):
        toolTip = ""
        if self.vars.has_key('bowler1') :
           toolTip = "\n{0} : {1}-{2}-{3}-{4}".format(self.vars['bowler1'], self.vars['bowler1overs'], self.vars['bowler1maidens'],self.vars['bowler1runs'],  self.vars['bowler1wickets'])
        if self.vars.has_key('bowler2') :
           toolTip = toolTip +  "\n{0} : {1}-{2}-{3}-{4}".format(self.vars['bowler2'], self.vars['bowler2overs'], self.vars['bowler2maidens'], self.vars['bowler2runs'],  self.vars['bowler2wickets'])
        return toolTip
    
    def notify(self, title, message):
          pynotify.init("Cricket Score Applet")
          n = pynotify.Notification(title, message)
          logging.log(logging.WARNING,"Time Out %s", self.notificationTimeOut)
          n.set_timeout(self.notificationTimeOut)
          n.set_urgency(pynotify.URGENCY_NORMAL)
          n.show()


class ScoreApplet():
    def __init__(self, applet):
                self.selectedMatchUrl = ""
                self.isInit = None
                self.score = Score()
                self.applet = applet
                self.toggle = gtk.ToggleButton()
                button_box = gtk.HBox()
                self.label = gtk.Label("Cric Score")
                button_box.pack_start(self.label)
                self.toggle.add(button_box)
                self.applet.add(self.toggle)
                self.toggle.connect("button-press-event", self._onButtonPress)
                self.applet.set_background_widget(self.applet)
                self.applet.setup_menu_from_file (gnome_cricscore_globals.datadir, "GNOME_CricScoreApplet.xml",
                                   None, [(("About"), self._showAboutDialog), ("Pref", self._openPrefs)])
                self.applet.show_all()
        
    def _openPrefs(self, uicomponent, verb):
                self._showPrefDialog()
   
    def _showAboutDialog(self, uicomponent, verb):
                gnome.ui.About(gnome_cricscore_globals.name, gnome_cricscore_globals.version, "Copyright 2010 Sachin Patil",
                       _("A GNOME Cricket Score Applet"), ["Sachin Patil <sachin6870 at gmail.com>"], [],
                       "", gtk.gdk.pixbuf_new_from_file(gnome_cricscore_globals.image_dir + "/cricscore.png")).show()

    def _showPrefDialog(self):
          prefs_dialog = cricscore_prefs.CricScorePrefs(self)
          prefs_dialog.show()
          prefs_dialog.run()
          prefs_dialog.hide()
    
    def _onButtonPress(self, toggle, event):
          if event.button != 1:
            toggle.stop_emission("button-press-event")
      
    def matchSelectionChanged(self, selectedMatchUrl):
        self.score.selectedMatchUrl = selectedMatchUrl
        self.score.state = State.SelectionChanged
        #self.update();
        
    def setShowScoreUpdate(self, showScoreUpdate):
        logging.log(logging.DEBUG, "showScoreUpdate Flag changed %s", showScoreUpdate)
        self.score.showScoreUpdate = showScoreUpdate
        
    def getShowScoreUpdate(self):
        return self.score.showScoreUpdate
    
    def setNotificationTimeOut(self, notificationTimeOut):
        logging.log(logging.DEBUG, "Notification TimeOut changed %s", str(self.score.notificationTimeOut))
        self.score.notificationTimeOut = notificationTimeOut
        
    def getNotificationTimeOut(self):
        return self.score.notificationTimeOut
    
    def update(self):
                logging.log(logging.DEBUG, "update called")
                if self.score.state == State.NotSelected:
                  self.label.set_text("Match is not selected")
                  self.label.set_tooltip_text("select match from Preferences")
                  return
                try:
                   logging.log(logging.DEBUG, 'calling refresh')
                   self.score.refresh()
                   if(self.score.state == State.Preview):
                     self.label.set_text("Match not yet started")
                     self.label.set_tooltip_text("Match not yet started")
                     return
                   self.label.set_text(self.score.getBatTeamScore())
                   self.label.set_tooltip_text(self.score.getTooltip() +  self.score.getTooltip1())
                except IOError: 
                    self.label.set_text("Cricket Score")
                    self.label.set_tooltip_text("No Internet Connection")
                    logging.log(logging.DEBUG, "No Internet Connection", sys.exc_info()[0]);
                except :
                    logging.log(logging.WARNING, "Unexpected error: %s", sys.exc_info()[0]); 
                    self.label.set_text("Cricket Score")
                    self.label.set_tooltip_text("Unexpected error")
                    
                if not self.isInit: 
                   logging.log(logging.DEBUG, "Initilizing")
                   self.isInit = gobject.timeout_add_seconds(30, self.update)
                    
                return True

def sample_factory(applet, iid):
    ScoreApplet(applet)
    return True

if len(sys.argv) == 2 and sys.argv[1] == "w":
    logging.basicConfig (stream = sys.stdout,
    level = logging.DEBUG,
    format = LOG_FORMAT)
    logging.log(logging.DEBUG, "running in window")
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("Cricket Score Applet")
    main_window.connect("destroy", gtk.main_quit) 
    app = gnomeapplet.Applet()
    sample_factory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()
    sys.exit()   
     
arg = sys.argv[1]    
if arg.startswith ("--oaf-activate-iid=") or arg.startswith ("--oaf-ior-fd="):
    #Setup Log files
    dirname = gnome_cricscore_globals.logdir
    logfile = file (os.path.join (dirname, "cricscore.log"), "w")
    sys.stdout = logfile
    sys.stderr = logfile
    logging.basicConfig (stream = logfile,
    level = logging.DEBUG,
    format = LOG_FORMAT)
    

gnomeapplet.bonobo_factory("OAFIID:GNOME_CricketScoreApplet_Factory",
                                gnomeapplet.Applet.__gtype__,
                                "cricscore", "0", sample_factory)


