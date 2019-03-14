#!/usr/bin/env python3

import sys
import re
from urllib.request import urlopen
import requests

# SoundCloud streaming Client ID
CLIENTID="NmW1FlPaiL94ueEu7oziOWjYEzZzQDcK"

def download_file(url, filename):
  f = urlopen(url)
  with open(filename, "wb") as song:
    song.write(f.read())

def get_title(title):
  # Cleans a title from Soundcloud to be filesystem friendly.
  allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789-_()$"
  return ''.join(c for c in title if c in allowed)

def is_valid_url(url):
  return re.match(r'^https*://(www.)*soundcloud\.com/', url)

def get_title(html):
  # What if the song title contains a '|' character?
  title_re = re.search('<title>([^|]+) | Free Listening on SoundCloud</title>',
      html.text, re.IGNORECASE)
  
  if title_re:
    return title_re.group(1)
  else:
    print("Error getting song title")
    return False

def get_sid(html):
  id_re = re.search(r'soundcloud://sounds:(\d+)', html.text, re.IGNORECASE)
  
  if id_re:
    return id_re.group(1)
  else:
    print("Error getting song id")
    return False

def main():
  song_url = sys.argv[1]
  if not is_valid_url(song_url):
    print("URL not valid")
    exit(1)

  html = requests.get(song_url)
  title = get_title(html)
  if not title:
    exit(1)
  
  song_id = get_sid(html)
  if not song_id:
    exit(1)
  
  stream_url = "https://api.soundcloud.com/i1/tracks/{0}/streams?client_id={1}".format(song_id, CLIENTID)  
  json_stream = requests.get(stream_url)
  download_file(json_stream.json()['http_mp3_128_url'], "{0}.mp3".format(title))

if __name__ == "__main__":
  main()

