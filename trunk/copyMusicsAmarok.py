# -*- coding: utf-8 -*-
"""
    Copyright (C) 2011 Renato "Lond" Cerqueira <lond@dcc.ufrj.br>
    Based on the source of elord, for 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from xml.dom import minidom
import MySQLdb
import os
import subprocess
from subprocess import Popen
import sys
import re
import shutil

VERBOSE = False
if "--verbose" in sys.argv:
	VERBOSE = True

dbpath = "/var/run/mysqld/mysqld."
dbpass = "password"
dbuser = "amarokuser"

socketpath = dbpath + "sock"
dbname = "amarokdb"

#used database interaction
updateQuery = "UPDATE statistics SET playcount=playcount+1 WHERE url=%s"
insertionQuery = "INSERT INTO statistics (playcount, url) VALUES (%s, %s)"
statisticsQuery = "SELECT * FROM statistics WHERE url="
allTracksQuery = "SELECT * FROM playlist_tracks ORDER BY artist, title" 
getPathQuery = "SELECT rpath, id FROM urls WHERE uniqueid=%s"

#Updates the database, connection is connection to the amarok DB
def updateDatabase(connection):
	artistsCursor = connection.cursor()
	tagsCursor = connection.cursor()
	statisticsCursor = connection.cursor()
	tracksCursor = connection.cursor()
	rpathCursor = connection.cursor()

	tracksCursor.execute(allTracksQuery) #get tracks in the playlist
  
	for track in tracksCursor:
		trackurl = track[3]
		rpathCursor.execute(getPathQuery, trackurl)
		for path in rpathCursor:
			print "Path for "+track[4]+" is "+path[0]
			myhome2="."+os.path.expanduser('~')+'/musicas/'
			myhome="."+os.path.expanduser('~')+'/musicas2/'
			try:mypath=re.sub(myhome2, "", re.sub(myhome, "", path[0]))
			except:print "fuu!"
			try:os.makedirs(os.path.dirname("/media/disk/Music/"+mypath))
			except:print "directory already exists"
			
			nupath = re.sub("^\.","",path[0])
			print nupath
			print path[1]
			
			try:
				shutil.copy(nupath, "/media/disk/Music/"+mypath)
				
				statisticsCursor.execute(statisticsQuery + str(path[1]))
				if statisticsCursor.rowcount == 0:
					statisticsCursor.execute(insertionQuery,(1, path[1]))
				else:
					statisticsCursor.execute(updateQuery, path[1])
			except:print sys.exc_info()


connection = MySQLdb.connect(unix_socket=socketpath, user=dbuser, passwd=dbpass, db=dbname ) #connect to the server

try: updateDatabase(connection)
except: print "Error in communication."
#finally: server.terminate()