#!/usr/bin/python2
import urllib2, sys, re
import urllib

if len(sys.argv) <= 1:
	exit("You need to enter a URI to download from")

def get_dl_url(htmlsource):
	regexp = "<img\ class=([\"\'])\waveform([\"\'])(.*?)>"

	for match in re.finditer(regexp, htmlsource):
		image = repr(match.group())
		break

	id = re.split('http://(.*?)/(.*?)_m.png"', image)[2]

	url = "http://media.soundcloud.com/stream/%s" % id

	return url

def get_title(htmlsource):
	regexp = "<title>(.*?)</title>"

	for match in re.finditer(regexp, htmlsource):
		title = repr(match.group())
		break
	
	title = re.split('<title>(.*?)</title>', title)[1].split(' on SoundCloud')[0]
	
	title = title.replace('by', '-')
	return "%s.mp3" % title

def main():
	print "Getting Information... "
	soundcloud_url = sys.argv[-1]
	try:
		html = urllib2.urlopen(soundcloud_url)
	except ValueError:
		exit("Error: The URL '%s' can not be retrieved" % soundcloud_url)
	htmlsource = html.read()
	html.close()
	
	title = get_title(htmlsource)
	url = get_dl_url(htmlsource)
	
	print "Downloading File '%s'" % title
	urllib.urlretrieve(url, title)
	print "Download Complete"

if __name__ == '__main__':
	main()
