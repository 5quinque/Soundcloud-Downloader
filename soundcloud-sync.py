#!/usr/bin/python
# March 8, 2014
import urllib, urllib2
import argparse
import requests
import os.path
import soundcloud
import os
import json
soundcloud_downloader = __import__('soundcloud-downloader')


class SoundCloudUser:
	def __init__(self, username):
		self.username = username
		self.userAPI = self.getUserAPI(username)
		self.playlists = self.getPlaylists()
	
	def getUserAPI(self, username):
		api="http://api.soundcloud.com/resolve.json?url=https://soundcloud.com/"+username+"&client_id=YOUR_CLIENT_ID".format()	
		response=requests.get(api)
		
		try:
			return response.json()['uri']
		except:
			print "User: " + username + " was not found. Please try again with a different user."
			sys.exit()
	
	def getPlaylists(self):
		api=self.userAPI + '/playlists.json?client_id=YOUR_CLIENT_ID'
		response=requests.get(api)

		playlists=[]
		for playlist in response.json():
			playlists.append(playlist['permalink_url'])

		return playlists
		 
if __name__ == "__main__":
   if (int(requests.__version__[0]) == 0):
      print "Your version of Requests needs updating\nTry: '(sudo) pip install -U requests'"
      sys.exit()

   # parse arguments
   parser = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", help="increase output verbosity",
      action="store_true")
   parser.add_argument("-t", "--id3tags", help="add id3 tags",
      action="store_true")
   parser.add_argument("USER", help="Soundcloud USER")
   parser.add_argument("TOP_LEVEL_MUSIC_DIR", help="Full path to your top directory")
   args = parser.parse_args()
   verbose = bool(args.verbose)
   tags = bool(args.id3tags)
   user = SoundCloudUser(args.USER)
	 
	 
   first_time=0
	 #Check if top level music directory exists
   if not os.path.isdir(args.TOP_LEVEL_MUSIC_DIR):
      os.makedirs(args.TOP_LEVEL_MUSIC_DIR)
      os.system('touch \''+ args.TOP_LEVEL_MUSIC_DIR+'/whitelist\'')
      first_time=1
	 
   if not os.path.isfile(args.TOP_LEVEL_MUSIC_DIR+'/whitelist'):
      os.system('touch \''+ args.TOP_LEVEL_MUSIC_DIR+'/whitelist\'')
      first_time=1
	 
   os.chdir(args.TOP_LEVEL_MUSIC_DIR)	  
   for playlist in user.playlists:
      playlist_folder=playlist.split('/')[-1] 
      if not os.path.isdir(args.TOP_LEVEL_MUSIC_DIR+'/'+playlist_folder):
         os.makedirs(args.TOP_LEVEL_MUSIC_DIR+'/'+playlist_folder)
				
      if playlist_folder in open(args.TOP_LEVEL_MUSIC_DIR+'/whitelist').read():
         continue  

      if first_time:
         with open(args.TOP_LEVEL_MUSIC_DIR+'/whitelist', "ab") as myfile:
            myfile.write(playlist_folder+'\n')
         continue						 

      os.chdir(args.TOP_LEVEL_MUSIC_DIR+'/'+playlist_folder)	  
      download = soundcloud_downloader.SoundCloudDownload(playlist, verbose, tags)
      download.downloadSongs()

   if first_time:
      print "**      This was the first time you ran this script with this directory"
      print "**      Your folder structrue was initilized. "
      print "**      Please find the whitelist file in folder: " + args.TOP_LEVEL_MUSIC_DIR
      print "**      Remove the playlists from the whitelist that you'd like to download" 	
      print "**      Then run the script again. :)"
