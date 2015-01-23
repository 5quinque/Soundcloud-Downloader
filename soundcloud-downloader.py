#!/usr/bin/python
# January 22, 2015
import urllib #update this eventually
import sys
import argparse #only include if you keep __main__
import re
import time
import os.path
import math
import os
import getpass
import datetime

import requests
try:
	import soundcloud
except ImportError:
	pass
try:
	from mutagen.mp3 import MP3
	from mutagen.id3 import ID3, APIC, TIT2, TPE1
except ImportError:
	pass

class SoundCloudDownload:
	
	def __init__(self, url, verbose, tags, artwork, limit=200, clientid='', clientsecret=''):
		if self.isValidSCUrl(url):
			self.url = url
		else:
			print('ERROR: Invalid SoundCloud URL')
			exit()
		self._client_id=clientid
		self._client_secret=clientsecret
		self.scclient = None
		try:
			if soundcloud:
				self.scclient = soundcloud.Client(client_id=self._client_id)#provide simple client object to start off with
		except NameError:#only raised in python3
			pass
		self.verbose = verbose
		if tags and not MP3:
			print('WARNING: Tags cannot be assigned without mutagen module')
			tags = False
			artwork = False
		self.tags = tags
		self.artwork = artwork
		self.download_progress = 0
		self.current_time = time.time()
		self.titleList = []
		self.artistList = []
		self.artworkURLList = []
		self.likes = False
		self.stream = False
		if limit < 201 and limit > 0:
			self.limit = limit
		else:
			self.limit = 200
		self.streamURLlist = self.getStreamURLlist(self.url)
	
	def getStreamURLlist(self, url):
		streamList = []
		tracks = []
		if url[-6:] == "/likes":
			url = url[:-6]
			self.likes = True
		if url[-7:] == "/stream":
			url = url[:-7]
			self.stream = True
		if not self.stream:
			if self.scclient:
				req = self.scclient.get('/resolve', url=url)
			else:
				api = "http://api.soundcloud.com/resolve.json?url={0}&client_id={1}".format(url, self._client_id)
				r = requests.get(api)
			try:
				if self.scclient:
					user = req.username #check resource is username resource
					user = req.id #overwrite with UID
				else:
					user = r.json()['username']
					user = r.json()['id']
				if self.likes:
					if self.scclient:
						span = math.ceil(req.public_favorites_count/float(200))
					else:
						span = math.ceil(r.json()['public_favorites_count']/float(200))
				else:
					if self.scclient:
						span = math.ceil(req.track_count/float(200))
					else:
						span = math.ceil(r.json()['track_count']/float(200))
				for x in range(0, int(span)):
					if self.likes:
						if self.scclient:
							api = self.scclient.get("/users/" + str(user) + "/favorites", limit=self.limit, offset=str(x * 200))
						else:
							api = "http://api.soundcloud.com/users/" + str(user) + "/favorites.json?client_id=" + self._client_id + "&limit=200&offset=" + str(x * 200)
					else:
						if self.scclient:
							api = self.scclient.get("/users/" + str(user) + "/tracks", limit=self.limit, offset=str(x * 200))
						else:
							api = "http://api.soundcloud.com/users/" + str(user) + "/tracks.json?client_id=" + self._client_id + "&limit=200&offset=" + str(x * 200)
					if self.scclient:
						tracks.extend(api)
					else:
						r = requests.get(api)
						tracks.extend(r.json())
			except:
				try:
					if self.scclient:
						tracks = req.tracks
					else:
						tracks = r.json()['tracks']
					# If this isn't a playlist, just make a list of
					# a single element (the track)
				except:
					if self.scclient:
						tracks = req
					else:
						tracks = [r.json()]
		else:
			if self.scclient: #possibly can be done without soundcloud API module but I don't have that much time to play around
				print("Please give the program access to your stream by logging in.")
				sys.stdout.write("Username(Email Address): ")
				Username = self.verInput()
				Password = getpass.getpass()
				try:
					self.scclient = soundcloud.Client(
						client_id=self._client_id,
						client_secret=self._client_secret,
						username=Username,
						password=Password
					)
				except:
					print("Password or Username was incorrect")
					exit()
				trackjsondata = self.scclient.get('/me/activities/tracks/affiliated', limit=self.limit)
				for track in trackjsondata.collection:
					tracks.append(track.origin)
			else:
				print("Can't get your user stream without soundcloud API")
				exit()
		resources = []
		try:
			resources.extend(tracks)#throws not iterable if single
		except:
			resources.append(tracks)
		#for track in tracks:
		regex = re.compile("\/([a-zA-Z0-9]+)_")#call compile before loop to avoid repeat compilation
		for track in resources:
			try:
				if self.scclient:
					waveform_url = track.waveform_url
					self.artworkURLList.append(track.artwork_url)
					self.titleList.append(self.getTitleFilename(track.title))
					self.artistList.append(track.user['username'])
				else:
					waveform_url = track['waveform_url']
					self.artworkURLList.append(track['artwork_url'])
					self.titleList.append(self.getTitleFilename(track['title']))
					self.artistList.append(track['user']['username'])
				r = regex.search(waveform_url)
				stream_id = r.groups()[0]
				streamList.append("http://media.soundcloud.com/stream/{0}".format(stream_id))
			except AttributeError:#if tracks are from stream, skip any non track
				pass
		return streamList

	def addID3(self, title, artist, artworkURL):
		flname = "{0}.mp3".format(self.getTitleFilename(title))
		id3nfo = MP3(flname, ID3=ID3)
		id3nfo.add_tags()
		# Slicing is to get the whole track name
		# because SoundCloud titles usually have
		# a dash between the artist and some name
		split = title.find("-")
		if not split == -1:
			id3nfo.tags.add(TIT2(encoding=3, text=title[(split + 2):]))
			id3nfo.tags.add(TPE1(encoding=3, text=title[:split]))
		else:
			id3nfo.tags.add(TIT2(encoding=3, text=title))
			id3nfo.tags.add(TPE1(encoding=3, text=artist))
		if self.artwork and artworkURL:
			DldRes = self.downloadCoverImage((self.getTitleFilename(title) + " - Cover"), artworkURL)
			if DldRes[0]:
				id3nfo.tags.add(
					APIC(
						encoding=3, # 3 is for utf-8
						mime='image/jpeg', # image/jpeg or image/png
						type=3, # 3 is for the cover image
						desc=u'Cover',
						data=open(DldRes[1], 'rb').read()
					)
				)
		else:
			if not artworkURL and self.verbose:
				print("Artwork for " + self.getTitleFilename(title) + " is not available")
		id3nfo.save(flname, v2_version=3, v1=2)
		if DldRes[0]:
			os.remove(DldRes[1])
		if self.verbose:
			print("\nID3 tags added")

	def downloadCoverImage(self, filename, artworkURL):
		filename = "{0}.jpg".format(self.getTitleFilename(filename))
		sys.stdout.write("\nDownloading: {0}\n".format(filename))
		try:
			if not os.path.isfile(filename):
				if self.verbose:
					filename, headers = urllib.urlretrieve(url=artworkURL, filename=filename, reporthook=self.report)
				else:
					filename, headers = urllib.urlretrieve(url=artworkURL, filename=filename)
				# reset download progress to report multiple track download progress correctly
				self.download_progress = 0
				return (True, filename) #tuple for fixed size and speed increase
			else:
				print("File Exists")
				return (True, filename)
		except:
			print("ERROR: Image is not retrievable.")
			return (False, None)

	def downloadAudio(self):
		done = False
		for artist, title, streamURL, artworkURL in zip(self.artistList, self.titleList, self.streamURLlist, self.artworkURLList):
			if not done:
				filename = "{0}.mp3".format(self.getTitleFilename(title))    
				sys.stdout.write("\nDownloading: {0}\n".format(filename))
				try:
					if not os.path.isfile(filename):
						if sys.version_info[0] == 3:
							if self.verbose:
								filename, headers = urllib.request.urlretrieve(url=streamURL, filename=filename, reporthook=self.report)
							else:
								filename, headers = urllib.request.urlretrieve(url=streamURL, filename=filename)
						else:
							if self.verbose:
								filename, headers = urllib.urlretrieve(url=streamURL, filename=filename, reporthook=self.report)
							else:
								filename, headers = urllib.urlretrieve(url=streamURL, filename=filename)
						# reset download progress to report multiple track download progress correctly
						self.download_progress = 0
						if self.tags:
							self.addID3(title, artist, artworkURL)
					elif self.likes:
						print("File Exists")
						done = True
					else:
						print("File Exists")
				except:
					if self.verbose:
						print("UNEXPECTED ERROR: ", sys.exc_info()[0]) #debugging
					print("ERROR: Author has not set song to streamable, so it cannot be downloaded")
			
	def report(self, block_no, block_size, file_size):
		if int(file_size) > 0:#added for python3 non-static file_size
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
		#Cleans a title from Soundcloud to be filesystem friendly.
		allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789-_()"
		return ''.join(c for c in title if c in allowed)
	
	def verInput(self): #python 3 support
		if sys.version_info[0] == 3:
			return input()
		elif sys.version_info[0] == 2:
			return raw_input()
		else:
			print("ERROR: Can't get input handle\nplease try non-interactive mode.")
			exit()

	def isValidSCUrl(self, url):
		if re.match(r'^https*://(www.)*soundcloud\.com/', url):
			return True
		else:
			print(url)
			return False

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Download content from SoundCloud.')
	parser.add_argument('--d', action='store', dest='SoundCloudURL', help='URL for download')
	parser.add_argument('-v', action='store_true', default=False, dest='IsVerbose', help='Display verbose information')
	parser.add_argument('-t', action='store_true', default=False, dest='IncludeTags', help='Inject ID3 tag to downloaded file')
	parser.add_argument('-a', action='store_true', default=False, dest='IncludeArtwork', help='Include artwork in ID3 tag')
	parser.add_argument('-l', action='store_true', default=False, dest='GetTracksLimit', help='How many tracks to get if multiple')
	args = parser.parse_args()
	if args.SoundCloudURL == None:
		print('No arguments specified.')
		exit()
	else:
		download = SoundCloudDownload(args.SoundCloudURL, verbose=args.IsVerbose, tags=args.IncludeTags, artwork=args.IncludeArtwork, limit=args.GetTracksLimit)
		download.downloadAudio()
