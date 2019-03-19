#!/usr/bin/env python3

import sys
import re
from urllib.request import urlopen
import requests

class SoundCloudDownloader:
    def __init__(self):
        # SoundCloud streaming Client ID
        self.client_id = "NmW1FlPaiL94ueEu7oziOWjYEzZzQDcK"

    def download_file(self, url, filename):
        """ Download the file
        Parameters
        ----------
        url : str : stream url used to download
        filename : str : filename of the downloaded file
        """
        f = urlopen(url)
        with open(filename, "wb") as song:
            song.write(f.read())
    
    def clean_title(self, title):
        """ Cleans a title from Soundcloud to be filesystem friendly.
        Parameters
        ----------
        title : str : title to clean
        Returns
        -------
        str : cleaned title
        """
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789-_()$"
        return ''.join(c for c in title if c in allowed)
    
    def is_valid_url(self, url):
        """ Check if a url is a valid soundcloud url 
        Parameters
        ----------
        url : str : user provided url we want to test
        Returns
        -------
        bool : Returns true if it matches our regex, else false
        """
        return re.match(r'^https*://(www.)*soundcloud\.com/', url)
    
    def get_title(self, html):
        """ Get the title of the soundcloud song
        Parameters
        ----------
        html : str : All the HTML from the given soundcloud page
        Returns
        -------
        str/bool : Text between <title> tags or false
            if it can not find the title
        """
        # What if the song title contains a '|' character?
        title_re = re.search('<title>([^|]+) | Free Listening on SoundCloud</title>',
            html.text, re.IGNORECASE)
      
        if title_re:
            return self.clean_title(title_re.group(1))
        else:
            print("Error getting song title")
            return False
    
    def get_sid(self, html):
        """ Get the song ID used to download the song 
        Parameters
        ----------
        html : str : All the HTML from the given soundcloud page
        Returns
        -------
        str/bool : The song ID or False if it can not 
            be found
        """
        id_re = re.search(r'soundcloud://sounds:(\d+)', html.text, re.IGNORECASE)
      
        if id_re:
            return id_re.group(1)
        else:
            print("Error getting song id")
            return False

    def get_stream_url(self, sid):
        """ Create the stream URL used for download the song
        Parameters
        ----------
        sid : str : Song id used to build the stream url
        Returns
        -------
        str : The stream url
        """
        stream_url = "https://api.soundcloud.com/i1/tracks/{0}/streams?client_id={1}".format(sid, self.client_id)  
        json_stream = requests.get(stream_url)
        return json_stream.json()['http_mp3_128_url']

    def download(self, url):
        """ Download a soundcloud song
        Parameters
        ----------
        url : str : Soundcloud url
        """
        # Check if it's a valid soundcloud url
        if not self.is_valid_url(url):
            print("URL not valid")
            exit(1)
      
        # Get the html of the soundcloud song page
        html = requests.get(url)

        # Get the song title
        title = self.get_title(html)
        if not title:
            exit(1)
        
        # Get the song id
        song_id = self.get_sid(html)
        if not song_id:
            exit(1)
        
        # Get the stream url
        stream_url = self.get_stream_url(song_id)

        # Download and save the song locally
        self.download_file(stream_url, "{0}.mp3".format(title))



def main():
    sc_downloader = SoundCloudDownloader()
    song_url = sys.argv[1]

    sc_downloader.download(song_url)

if __name__ == "__main__":
    main()

