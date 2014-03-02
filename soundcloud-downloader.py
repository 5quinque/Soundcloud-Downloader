#!/usr/bin/python
# 25/04/13
import urllib, urllib2
import sys
import argparse
import re
import requests
import time

from ID3 import *

class SoundCloudDownload:
	def __init__(self, url, verbose, tags):
		self.url = url
		self.verbose = verbose
		self.tags = tags
		self.download_progress = 0
		self.current_time = time.time()
		self.download_progress = 0
		self.title = ''
		self.streamURL = self.getStreamURL(self.url)
	
	def getStreamURL(self, url):
		r = requests.get("http://api.soundcloud.com/resolve.json?url={0}&client_id=YOUR_CLIENT_ID".format(url))
		waveform_url = r.json()['waveform_url']
		self.title = r.json()['title']
		regex = re.compile("\/([a-zA-Z0-9]+)_")
		r = regex.search(waveform_url)
		stream_id = r.groups()[0]
		return "http://media.soundcloud.com/stream/{0}".format(stream_id)

	def addID3(self):
		try:
			id3info = ID3("{0}.mp3".format(self.title))
			id3info['TITLE'] = self.title
			id3info['ARTIST'] = self.title
			print "\nID3 tags added"
		except InvalidTagError, err:
			print "\nInvalid ID3 tag: {0}".format(err)
	
	def downloadSong(self):
		filename = "{0}.mp3".format(self.title)
		sys.stdout.write("\nDownloading: {0}\n".format(filename))
		filename, headers = urllib.urlretrieve(url=self.streamURL, filename=filename, reporthook=self.report)
		self.addID3()
	
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
	download.downloadSong()
	
	

