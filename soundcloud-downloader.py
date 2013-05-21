#!/usr/bin/python
# 25/04/13
import urllib, urllib2
import sys
import argparse
import re
import lxml.html
import time

from ID3 import *

class SoundCloudDownload:
	def __init__(self, url, verbose, tags, related):
		self.url = url
		self.verbose = verbose
		self.tags = tags
		self.related = related
		self.musicInfo = {}
		self.download_progress = 0
		
		self.getInfo(self.url)
	
	def addID3(self, filename, title, artist):
		try:
			id3info = ID3(filename)
			id3info['TITLE'] = title
			id3info['ARTIST'] = artist
			print "\nID3 tags added"
		except InvalidTagError, err:
			print "\nInvalid ID3 tag: {0}".format(err)
		
		return 0
	
	def makeURL(self, src):
		regexp = 'http://[^/]*/(\w*)_m.png'
		match = re.search(regexp, src)
		
		if match:
			songid = match.group(1)
			url = "http://media.soundcloud.com/stream/{0}".format(songid)
		else:
			sys.stderr.write("Stream URL not found for source {0}.\n".format(src))
		
		return url
	
	def downloadSong(self, title, src):
		valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
		url = self.makeURL(src)
		match = re.search("(.+)\sby\s(.+)\son\sSoundCloud.*", title)
		try:
			songTitle = match.group(1)
			artist = match.group(2).capitalize()
			songTitle = ''.join(c for c in songTitle if c in valid_chars)
			artist = ''.join(c for c in artist if c in valid_chars)
		except AttributeError:
			sys.stderr.write("\nError finding title\n")
			songTitle = "Not Found"
			artist = "Not Found"
			return 1
		mp3 = "{0} - {1}.mp3".format(songTitle, artist)
		sys.stdout.write("\nDownloading: {0}\n".format(mp3))
		filename, headers = urllib.urlretrieve(url=url, filename=mp3, reporthook=self.report)
		self.addID3(mp3, songTitle, artist)
	
	def getInfo(self, url):
		try:
			# Opens the URL
			self.html = lxml.html.parse(url)
		except IOError:
			# If the URL can not be read, exit
			sys.exit('Error: The URL \'{0}\' is borked'.format(url))
		
		# Retrieve the page's title
		pageTitle = self.html.xpath('//title/text()')[0]
		musicSrc = self.html.xpath("//img[@class='waveform']/@src")[0]
		self.musicInfo[pageTitle] = musicSrc
		
		return 0
	
	def report(self, block_no, block_size, file_size):
		self.download_progress += block_size
		if int(self.download_progress / 1024 * 8) > 1000:
			speed = "{0} Mbps".format(round((self.download_progress / 1024 / 1024 * 8) / (time.time() - self.current_time), 2))
		else:
			speed = "{0} Kbps".format(round((self.download_progress / 1024 * 8) / (time.time() - self.current_time), 2))
		rProgress = round(self.download_progress/1024.00/1024.00, 2)
		rFile = round(file_size/1024.00/1024.00, 2)
		percent = round(100 * float(self.download_progress)/float(file_size))
		sys.stdout.write("\r {3} ({0:.2f}/{1:.2f}MB): {2:.2f}% ".format(rProgress, rFile, percent, speed))
		sys.stdout.flush()

def main(url, verbose, tags, related):
	down = SoundCloudDownload(url, verbose, tags, related)
	
	if down.related:
		down.relatedURLs = down.html.xpath("//div[contains(@class, 'player')]//h3//a/@href")
		for i in range(len(down.relatedURLs)):
				if not down.relatedURLs[i].startswith('http://soundcloud.com'):
					down.relatedURLs[i] = 'http://soundcloud.com{0}'.format(down.relatedURLs[i])
		for a in down.relatedURLs:
			down.getInfo(a)
	for mp3 in down.musicInfo:
		down.download_progress = 0
		down.current_time = time.time()
		down.downloadSong(mp3, down.musicInfo[mp3])
		sys.stdout.write("Downloaded in: {0} Seconds\n".format(round(time.time() - down.current_time, 2)))
	
	return 0

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

