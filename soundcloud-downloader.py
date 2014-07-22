#!/usr/bin/python
# March 8, 2014
import urllib, urllib2
import sys
import argparse
import re
import requests
import time
import os.path
import soundcloud
import math
import os

from ID3 import *

class SoundCloudDownload:
   def __init__(self, url, verbose, tags):
      self.url = url
      self.verbose = verbose
      self.tags = tags
      self.download_progress = 0
      self.current_time = time.time()
      self.titleList = []
      self.artistList = []
      self.likes = False   
      self.streamURLlist = self.getStreamURLlist(self.url)

   def getStreamURLlist(self, url):
      streamList = []
      tracks = []
      if "/likes" in url:
         url = url[:-6]
         self.likes = True
      api = "http://api.soundcloud.com/resolve.json?url={0}&client_id=YOUR_CLIENT_ID".format(url)
      r = requests.get(api)
      try:
         user = r.json()['username']
         user = r.json()['id']
         span = math.ceil(r.json()['public_favorites_count']/float(200)) if self.likes else math.ceil(r.json()['track_count']/float(200))

         for x in range(0, int(span)):
            if self.likes:
               api = "http://api.soundcloud.com/users/" + str(user) + "/favorites.json?client_id=fc6924c8838d01597bab5ab42807c4ae&limit=200&offset=" + str(x * 200)
            else:
               api = "http://api.soundcloud.com/users/" + str(user) + "/tracks.json?client_id=fc6924c8838d01597bab5ab42807c4ae&limit=200&offset=" + str(x * 200)
            r = requests.get(api)
            tracks.extend(r.json())
      except:
         try:
            tracks = r.json()['tracks']
            # If this isn't a playlist, just make a list of
            # a single element (the track)
         except:
            tracks = [r.json()]
      for track in tracks:
         waveform_url = track['waveform_url']
         self.titleList.append(self.getTitleFilename(track['title']))
         self.artistList.append(track['user']['username'])
         regex = re.compile("\/([a-zA-Z0-9]+)_")
         r = regex.search(waveform_url)
         stream_id = r.groups()[0]
         streamList.append("http://media.soundcloud.com/stream/{0}".format(stream_id))
      return streamList

   def addID3(self, title, artist):
      try:
         id3info = ID3("{0}.mp3".format(title))
         # Slicing is to get the whole track name
         # because SoundCloud titles usually have
         # a dash between the artist and some name
         split = title.find("-")
         if not split == -1:
            id3info['TITLE'] = title[(split + 2):] 
            id3info['ARTIST'] = title[:split] 
         else:
            id3info['TITLE'] = title
            id3info['ARTIST'] = artist
         print "\nID3 tags added"
      except InvalidTagError, err:
         print "\nInvalid ID3 tag: {0}".format(err)
   
   def downloadSongs(self):
      done = False
      for artist, title, streamURL in zip(self.artistList, self.titleList, self.streamURLlist):
         if not done:
            filename = "{0}.mp3".format(title)
            sys.stdout.write("\nDownloading: {0}\n".format(filename))
            try:
               if not os.path.isfile(filename):
                  filename, headers = urllib.urlretrieve(url=streamURL, filename=filename, reporthook=self.report)
                  self.addID3(title, artist)
                  # reset download progress to report multiple track download progress correctly
                  self.download_progress = 0
               elif self.likes:
                  print "File Exists"
                  done = True
               else:
                  print "File Exists"
            except:
               print "ERROR: Author has not set song to streamable, so it cannot be downloaded"
   
   def report(self, block_no, block_size, file_size):
      self.download_progress += block_size
      if int(self.download_progress / 1024 * 8) > 1000:
         speed = "{0} Mbps".format(round((self.download_progress / 1024 / 1024 * 8) / (time.time() - self.current_time), 2))
      else:
         speed = "{0} Kbps".format(round((self.download_progress / 1024 * 8) / (time.time() - self.current_time), 2))
      rProgress = round(self.download_progress/1024.00/1024.00, 2)
      rFile = round(file_size/1024.00/1024.00, 2)
      percent = round(100 * float(self.download_progress)/float(file_size))
      sys.stdout.write("\r {3} ({0:.2f}/{1:.2f}MB): {2:.2f}%".format(rProgress, rFile, percent, speed))
      sys.stdout.flush()

        ## Convenience Methods
   def getTitleFilename(self, title):
                '''
                Cleans a title from Soundcloud to be a guaranteed-allowable filename in any filesystem.
                '''
                allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789-_()"
                return ''.join(c for c in title if c in allowed)

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
   parser.add_argument("SOUND_URL", help="Soundcloud URL")
   args = parser.parse_args()
   verbose = bool(args.verbose)
   tags = bool(args.id3tags)
   download = SoundCloudDownload(args.SOUND_URL, verbose, tags)
   download.downloadSongs()
