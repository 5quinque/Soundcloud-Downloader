#!/usr/bin/python
# 25/04/13
import urllib, urllib2
import sys
import argparse
import re
import lxml.html

from ID3 import *

class SoundCloudDownload:
	def __init__(self, url, verbose, tags, related):
		self.url = url
		self.verbose = verbose
		self.tags = tags
		self.related = False # Keep it false until it works # = related
		
		self.download_progress = 0
		
		try:
			# Opens the URL
			self.html = lxml.html.parse(self.url)
		except IOError:
			# If the URL can not be read, exit and inform the silly cunt
			sys.exit('Error: The URL \'{0}\' is borked'.format(self.url))
		
		# Retrieve the page's title
		self.pageTitle = self.html.xpath('//title/text()')[0]
		self.musicSrc = self.html.xpath("//img[@class='waveform']/@src")
		
		if not self.related:
			# Only have the first source in the list
			# The titles, wot about the titles??????
			self.musicSrc = self.musicSrc[:1]
		
	def add_id3_tags(self, filename, title, artist):
		try:
			id3info = ID3(filename)
			id3info['TITLE'] = title
			id3info['ARTIST'] = artist
			print "\nID3 tags added"
		except InvalidTagError, message:
			print "Invalid ID3 tag:", message
		
		return 0
	
	def makeURL(self, src):
		regexp = 'http://[^/]*/(\w*)_m.png'
		match = re.search(regexp, src)
		
		if match:
			songid = match.group(1)	
			url = "http://media.soundcloud.com/stream/%s" % songid
		else:
			sys.exit("No waveform image found at %s. Exiting." % sys.argv[1])
		
		return url
	
	def downloadSong(self, src):
		url = self.makeURL(src)
		match = re.search("(.*?)\sby\s([\w'\s]*)\son\sSoundCloud.*", self.pageTitle)
		songTitle = match.group(1)
		artist = match.group(2).capitalize()
		mp3 = "{0} - {1}.mp3".format(songTitle, artist)
		filename, headers = urllib.urlretrieve(url=url, filename=mp3, reporthook=self.report)
		self.add_id3_tags(mp3, songTitle, artist)

	def report(self, block_no, block_size, file_size):
		self.download_progress += block_size
		rProgress = round(self.download_progress/1024.00/1024.00, 2)
		rFile = round(file_size/1024.00/1024.00, 2)
		percent = round(100 * float(self.download_progress)/float(file_size))
		sys.stdout.write("\rDownloading ({0:.2f}/{1:.2f}MB): {2:.2f}% / 100%".format(rProgress, rFile, percent))
		sys.stdout.flush()
	
def main(url, verbose, tags, related):
	down = SoundCloudDownload(url, verbose, tags, related)
	
	for src in down.musicSrc:
		down.downloadSong(src)

if __name__ == "__main__":
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--verbose", help="increase output verbosity",
		action="store_true")
	parser.add_argument("-t", "--id3tags", help="add id3 tags",
		action="store_true")
	parser.add_argument("-r", "--related", help="download related songs",
		action="store_true")
	parser.add_argument("SOUND_URL", help="Soundcloud URL")
	args = parser.parse_args()
	verbose = bool(args.verbose)
	tags = bool(args.id3tags)
	related = bool(args.related)
	
	main(args.SOUND_URL, verbose, tags, related)



