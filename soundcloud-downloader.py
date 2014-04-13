#!/usr/bin/python
# March 8, 2014
import urllib
import sys
import argparse
import re
import requests
import time
import os

from ID3 import *


class SoundCloudDownload:

    def __init__(self, args):
        self.url = args['SOUND_URL']
        self.verbose = args['verbose']
        self.tags = args['id3tags']
        self.output_dir = args[r'output_dir']
        self.overwrite = args['overwrite_files']
        self.download_progress = 0
        self.current_time = time.time()
        self.titleList = []
        self.create_folder = False

        self.streamURLlist = self.getStreamURLlist(self.url)

    def getStreamURLlist(self, url):
        try:
            r = requests.get("http://api.soundcloud.com/resolve.json?url={0}&client_id=YOUR_CLIENT_ID".format(url))
        except requests.ConnectionError:
            print 'Error connecting to Soundcloud.\nExiting.'
            sys.exit()
        streamList = []
        # Try to get the tracks in the playlist
        try:
            tracks = r.json()['tracks']
        # If this isn't a playlist, just make a list of
        # a single element (the track)
        except:
            tracks = [r.json()]
        for track in tracks:
            waveform_url = track['waveform_url']
            self.titleList.append(self.getTitleFilename(track['title']))
            regex = re.compile("\/([a-zA-Z0-9]+)_")
            r = regex.search(waveform_url)
            stream_id = r.groups()[0]
            streamList.append("http://media.soundcloud.com/stream/{0}".format(stream_id))
        return streamList

    def addID3(self, title):
        title, ext = os.path.splitext(os.path.basename(title))
        try:
            id3info = ID3("{0}.mp3".format(title))
            # Slicing is to get the whole track name
            # because SoundCloud titles are usually longer
            # than the ID3 spec of 30 characters
            id3info['TITLE'] = title[:30]  # first 30 chars
            id3info['ARTIST'] = title[30:]  # rest of the chars
            print "\nID3 tags added"
        except InvalidTagError, err:
            print "\nInvalid ID3 tag: {0}".format(err)

    def downloadSongs(self):
        for title, streamURL in zip(self.titleList, self.streamURLlist):
            filename = self.createFilename(title)
            sys.stdout.write("\nDownloading: {0}\n".format(filename))
            try:
                filename, headers = urllib.urlretrieve(url=streamURL, filename=filename, reporthook=self.report)
            except:
                # remove file if we can't connect to the stream
                os.remove(filename)
                # remove folder if we created it
                if self.create_folder:
                    os.rmdir(os.path.dirname(filename))
                print "ERROR: Author has not set song to streamable, so it cannot be downloaded"
            #//FIXME ID3 tagging doesn't work on Win8.1
            else:
                if self.tags:
                    self.addID3(filename)
                self.download_progress = 0

    def report(self, block_no, block_size, file_size):
        self.download_progress += block_size
        if int(self.download_progress / 1024 * 8) > 1000:
            speed = "{0} Mbps".format(
                round((self.download_progress / 1024 / 1024 * 8) / (time.time() - self.current_time), 2))
        else:
            speed = "{0} Kbps".format(round((self.download_progress / 1024 * 8) / (time.time() - self.current_time), 2))
        rProgress = round(self.download_progress / 1024.00 / 1024.00, 2)
        rFile = round(file_size / 1024.00 / 1024.00, 2)
        percent = round(100.0 * float(self.download_progress) / float(file_size), 2)
        sys.stdout.write("\r {3} ({0:.2f}/{1:.2f}MB): {2:.0f}%".format(rProgress, rFile, percent, speed))
        sys.stdout.flush()

    ## Convenience Methods
    def getTitleFilename(self, title):
        """
                Cleans a title from Soundcloud to be a guaranteed-allowable filename in any filesystem.
                """
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789-_()"
        # clean up multiple spaces with the dual join/split
        return ' '.join(''.join(c for c in title if c in allowed).split())


    def createFilename(self, title):
        """
            Tests if optional argument output directory exists.  Returns same directory if true,
            attempts to create directory if it doesn't.  Raises error if unable to create directory.
        """
        d = self.output_dir
        filename = "{0}.mp3".format(title)
        if d is None:
            # user didn't user output arguments, file will download in directory script ran
            d = os.getcwdu()
        else:
            d = os.path.expanduser(d)
            try:
                os.makedirs(d)
                self.create_folder = True
            except OSError:
                if not os.path.isdir(d):
                    # could not create directory; warn user and exit.
                    print "ERROR: Attempt to create {0} failed.\nExiting.".format(d)
                    sys.exit()
        f = filename
        if not self.overwrite:
        #     if user opted to overwrite files, test if file already exists.
        #     if file exists, append incremented number to filename
        #     prevents overwriting existing files
            count = 0
            while os.path.isfile(os.path.join(d, f)):
                count += 1
                f, ext = os.path.splitext(filename)
                f = '{0}_({1:02d}){2}'.format(f, count, ext)
        return os.path.join(d, f)




if __name__ == "__main__":
    if (int(requests.__version__[0]) == 0):
        print "Your version of Requests needs updating\nTry: '(sudo) pip install -U requests'"
        sys.exit()

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity; boolean, default is true",
                        action="store_true")
    parser.add_argument("-t", "--id3tags", help="add id3 tags; boolean, default is true",
                        action="store_true")
    parser.add_argument("-d", "--output_dir", help="directory where file(s) will be saved")
    parser.add_argument("-o", "--overwrite_files", help="overwrite existing files, default does not overwrite files",
                        action="store_true")
    parser.add_argument("SOUND_URL", help="Soundcloud URL")
    args = vars(parser.parse_args())

    download = SoundCloudDownload(args)
    download.downloadSongs()
