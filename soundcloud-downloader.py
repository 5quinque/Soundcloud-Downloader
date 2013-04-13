#!/usr/bin/python
# 13/04/13
import urllib2, sys, re
import urllib
#import urllib

if len(sys.argv) <= 1:
	exit("You need to enter a URI to download from")

def get_dl_url(htmlsource):
	# regular expression for the string we will search for in htmlsource 
	regexp = '<img class="waveform"\ssrc="http://(.+?)/(.*?)_m.png" unselectable="on" />'
	
	# find the first match that occurs, if any
	first_match = re.search(regexp, htmlsource)
	
	if first_match:
		# if we found a match, retrieve the song ID
		id = first_match.group(2)
		
		# create a new stream hyperlink with the song ID
		url = "http://media.soundcloud.com/stream/%s" % id
	else:
		print "No waveform image found at %s. Exiting." % sys.argv[1]
		sys.exit()
	
	return url

def get_title(htmlsource):
	# regular expression for the string we will search for in htmlsource
	regexp = "<title>(.*?)\son\sSoundCloud.*</title>"

	# find the first match that occurs, if any
	first_match = re.search(regexp, htmlsource)
	
	if first_match:
		# if we found a match, retrieve the title of the song
		title = first_match.group(1)
		
		# replace every occurrence of 'by' in the title with a hyphen
		title = title.replace('by', '-')
	else:
		print "No title data for song at %s. Exiting." % sys.argv[1]
		sys.exit()	
	
	return "%s.mp3" % title

def main():
	print "Getting Information... "
	
	# retrieve the URL of the song to download from the final command-line argument
	soundcloud_url = sys.argv[-1]
	
	try:
		# open our song's URL for reading
		html = urllib2.urlopen(soundcloud_url)
	except ValueError:
		# the user supplied URL is invalid or could not be retrieved 
		exit("Error: The URL '%s' can not be retrieved" % soundcloud_url)
		
	# store the contents (source) of our song's URL
	htmlsource = html.read()
	html.close()
	
	# get our song's title from its HTML contents
	title = get_title(htmlsource)
	
	# get our song's actual download URL from its HTML contents
	url = get_dl_url(htmlsource)
	
	print "Downloading File '%s'" % title
	
	# copy the download URL's content (the full song) to a file 
	# with a filename that matches our song's title
	#urllib.urlretrieve(url, title)
	filename, headers = urllib.urlretrieve(url=url, filename=title, reporthook=report)
	print "\n\nDownload Complete"

def report(block_no, block_size, file_size):
	global download_progress
	download_progress += block_size
	
	sys.stdout.write("\rDownloading (%.2fMB/%.2fMB): %.2f%% / 100%%" % (download_progress/1024/1024.00, file_size/1024.00/1024.00, 100 * float(download_progress)/float(file_size)) )
	sys.stdout.flush()

if __name__ == '__main__':
	download_progress = 0
	main()
