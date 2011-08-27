#!/usr/bin/python2
import urllib2, sys, re
import urllib

if len(sys.argv) <= 1:
	exit("You need to enter a URI to download from")

def get_dl_url(htmlsource):
	regexp = "<img [^\>]*class=([\"\'])\waveform([\"\'])(.*?)>"

	for match in re.finditer(regexp, htmlsource):
		image = repr(match.group())
		break

	id = image.split('src="')[1].split('"')[0].split('/')[3].split('_')[0]

	url = "http://media.soundcloud.com/stream/%s" % id

	return url

def get_title(htmlsource):
	regexp = "<title>(.*?)</title>"

	for match in re.finditer(regexp, htmlsource):
		title = repr(match.group())
		break
	
	title = title.split('<title>')[1].split('</title>')[0].split('on SoundCloud')[0]
	title = title.replace('by', '-')
	return title + ".mp3"

def main():
	print "Getting Information"
	soundcloud_url = sys.argv[-1]
	html = urllib2.urlopen(soundcloud_url)
	htmlsource = html.read()
	html.close()
	
	title = get_title(htmlsource)
	
	url = get_dl_url(htmlsource)
	
	print "Downloading File..."
	urllib.urlretrieve(url, title)

if __name__ == '__main__':
	main()
