#!/usr/bin/python
# November 18, 2015
import urllib  # update this eventually
import sys
import argparse  # only include if you keep __main__
import re
import math
import os
import getpass

# import booleans
soundcloudInstalled = True
mutagenInstalled = True

# Third-Party modules
import requests
try:
    import soundcloud
except ImportError:
    soundcloudInstalled = False
    pass
try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1
except ImportError:
    mutagenInstalled = False
    pass


class SoundCloudDownload:
    def __init__(self, url, verbose, tags, artwork, limit=20, clientid='YOUR_CLIENT_ID',
                 clientsecret='YOUR_CLIENT_SECRET'):
        self._maxlimit = 200
        limit = int(limit)
        if not self.isValidSCUrl(url):
            print('ERROR: Invalid SoundCloud URL')
            exit()
        self.url = url
        self._client_id = clientid
        self._client_secret = clientsecret
        self.scclient = None
        if soundcloudInstalled: self.scclient = soundcloud.Client(
            client_id=self._client_id)  # provide simple client object to start off with
        self.verbose = verbose
        if not mutagenInstalled and (tags or artwork):
            print('WARNING: Tags and/or artwork cannot be added to the mp3 without the mutagen module')
            tags = False
            artwork = False
        self.tags = tags
        self.artwork = artwork
        self.download_progress = 0
        self.titleList = []
        self.artistList = []
        self.artworkURLList = []
        self.likes = False
        self.stream = False
        self.limit = limit if limit > 0 else 20
        self.streamURLlist = self.getStreamURLList(self.url)

    def getStreamURLListWithoutSoundCloud(self, url):
        streamList = []
        tracks = []
        if not self.stream:
            api = "http://api.soundcloud.com/resolve.json?url={0}&client_id={1}".format(url, self._client_id)
            r = requests.get(api)
            try:
                user = r.json()['username']
                user = r.json()['id']
                countTerm = 'public_favorites_count' if self.likes else 'track_count'
                span = math.ceil(r.json()[countTerm] / float(self._maxlimit))
                for x in range(0, int(span)):
                    if self.limit < 1: break
                    searchTerm = "favorites" if self.likes else "tracks"
                    api = "http://api.soundcloud.com/users/{0}/{1}.json?client_id={2}&limit={3}&offset={4}".format(
                        str(user), searchTerm, self._client_id, str(self.limit), str(x * self._maxlimit))
                    r = requests.get(api)
                    tracks.extend(r.json())
                    self.limit -= self._maxlimit
            except:
                try:
                    tracks = r.json()[
                        'tracks']  # If this isn't a playlist, just make a list of a single element (the track)
                except:
                    tracks = [r.json()]
        else:
            print("Can't get your user stream without soundcloud API")
            exit()
        resources = []
        try:
            resources.extend(tracks)  # throws not iterable if single
        except:
            resources.append(tracks)
        regex = re.compile("\/([a-zA-Z0-9]+)_")  # call compile before loop to avoid repeat compilation
        for track in resources:
            try:
                waveform_url = track['waveform_url']
                self.artworkURLList.append(track['artwork_url'])
                self.titleList.append(self.getTitleFilename(track['title']))
                self.artistList.append(track['user']['username'])
                headers = {"Accept": "application/json", "User-Agent": "SoundCloud Python API Wrapper 0.5.0"}
                api = "{0}?client_id={1}".format(track['stream_url'], self._client_id)
                r = requests.get(api, allow_redirects=False, headers=headers)
                streamList.append(r.json()["location"])
            except AttributeError:  # if tracks are from stream, skip any non track
                pass
        return streamList

    def getStreamURLListWithSoundcloud(self, url):
        streamList = []
        tracks = []
        if not self.stream:
            req = self.scclient.get('/resolve', url=url)
            try:
                user = req.username  # check resource is username resource
                user = req.id  # overwrite with UID
                span = math.ceil(req.public_favorites_count / float(self._maxlimit)) if self.likes else math.ceil(
                    req.track_count / float(self._maxlimit))
                tracks_to_get = self.limit
                for x in range(0, int(span)):
                    if tracks_to_get < 1: break
                    searchTerm = "favorites" if self.likes else "tracks"
                    api = self.scclient.get("/users/{0}/{1}".format(user, searchTerm), limit=tracks_to_get,
                                            offset=str(x * self._maxlimit))
                    tracks.extend(api)
                    tracks_to_get -= self._maxlimit
            except:
                try:
                    tracks = req.tracks  # If this isn't a playlist, just make a list of a single element (the track)
                except:
                    tracks = req
        else:
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
        resources = []
        try:
            resources.extend(tracks)  # throws not iterable if single
        except:
            resources.append(tracks)
        regex = re.compile("\/([a-zA-Z0-9]+)_")  # call compile before loop to avoid repeat compilation
        for track in resources:
            try:
                if type(track) is not dict:  # double check resource is type resource
                    waveform_url = track.waveform_url
                    self.artworkURLList.append(track.artwork_url)
                    self.titleList.append(self.getTitleFilename(track.title))
                    self.artistList.append(track.user['username'])
                    stream_url = self.scclient.get(track.stream_url, allow_redirects=False)
                    streamList.append(stream_url.location)
            except AttributeError:
                pass  # if tracks are from stream, skip any non track
        return streamList

    def getStreamURLList(self, url):
        if url[-6:] == "/likes":
            url = url[:-6]
            self.likes = True
        elif url[-7:] == "/stream":
            url = url[:-7]
            self.stream = True
        return self.getStreamURLListWithSoundcloud(
            url) if soundcloudInstalled else self.getStreamURLListWithoutSoundCloud(url)

    def addID3(self, title, artist, artworkURL):
        flname = "{0}.mp3".format(self.getTitleFilename(title))
        id3nfo = MP3(flname, ID3=ID3)
        id3nfo.add_tags()
        # Slicing is to get the whole track name
        # because SoundCloud titles usually have
        # a dash between the artist and some name
        split = title.find("-")
        if not split == -1:
            artist = title[:split]
            title = title[(split + 2):]
        id3nfo.tags.add(TIT2(encoding=3, text=title))
        id3nfo.tags.add(TPE1(encoding=3, text=artist))
        if self.artwork and artworkURL:
            DldRes = self.downloadCoverImage((self.getTitleFilename(title) + " - Cover"), artworkURL)
            if DldRes[0]:
                id3nfo.tags.add(
                    APIC(
                        encoding=3,  # 3 is for utf-8
                        mime='image/jpeg',  # image/jpeg or image/png
                        type=3,  # 3 is for the cover image
                        desc=u'Cover',
                        data=open(DldRes[1], 'rb').read()
                    )
                )
        elif not artworkURL and self.verbose:
            print("Artwork for " + self.getTitleFilename(title) + " is not available")
        id3nfo.save(flname, v2_version=3, v1=2)
        if DldRes[0]: os.remove(DldRes[1])
        if self.verbose: print("ID3 tags added!")

    def downloadCoverImage(self, filename, artworkURL):
        filename = "{0}.jpg".format(self.getTitleFilename(filename))
        print("Downloading: {0}".format(filename))
        try:
            self.download(artworkURL, filename)
            return (True, filename)
        except:
            print("ERROR: Image is not retrievable.")
            return (False, None)

    def downloadAudio(self):
        for artist, title, streamURL, artworkURL in zip(self.artistList, self.titleList, self.streamURLlist,
                                                        self.artworkURLList):
            filename = "{0}.mp3".format(self.getTitleFilename(title))
            print("\nDownloading: {0}".format(filename))
            try:
                self.download(streamURL, filename)
                if self.tags: self.addID3(title, artist, artworkURL)
                print()
            except:
                if self.verbose:
                    print("ERROR: ", sys.exc_info()[0])  # debugging
                else:
                    print("ERROR: Author has not set song to streamable, so it cannot be downloaded")

    def download(self, link, file_name):
        if (os.path.isfile(file_name)):
            print('"' + file_name + "\" already exists.")
            return True
        try:
            req = None
            total_size = 0
            if sys.version_info[0] == 3:
                req = urllib.request.urlopen(link)
                total_size = int(req.getheader('Content-Length').strip())
            else:
                req = urllib.urlopen(link)
                total_size = int(req.info().getheader('Content-Length').strip())
            downloaded = 0
            CHUNK = 256 * 10240
            with open(file_name, 'wb') as fp:
                while True:
                    chunk = req.read(CHUNK)
                    downloaded += len(chunk)
                    if self.verbose:
                        done = int(50 * downloaded / total_size)
                        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                        sys.stdout.flush()
                    if not chunk: break
                    fp.write(chunk)
            if self.verbose: print()
        except urllib.error.HTTPError as e:
            print("HTTP Error:", e.code, link)
            return False
        except urllib.error.URLError as e:
            print("URL Error:", e.reason, link)
            return False
        return True

    ## Convenience Methods
    def getTitleFilename(self, title):
        # Cleans a title from Soundcloud to be filesystem friendly.
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789-_()$"
        return ''.join(c for c in title if c in allowed)

    def verInput(self):  # python 3 support
        if sys.version_info[0] == 3:
            return input()
        else:
            return raw_input()

    def isValidSCUrl(self, url):
        return True if re.match(r'^https*://(www.)*soundcloud\.com/', url) else False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download content from SoundCloud.')
    parser.add_argument('--d', action='store', dest='SoundCloudURL', help='URL for download')
    parser.add_argument('-v', action='store_true', default=False, dest='IsVerbose', help='Display verbose information')
    parser.add_argument('-t', action='store_true', default=False, dest='IncludeTags',
                        help='Inject ID3 tag to downloaded file')
    parser.add_argument('-a', action='store_true', default=False, dest='IncludeArtwork',
                        help='Include artwork in ID3 tag')
    parser.add_argument('--l', action='store', default=20, dest='GetTracksLimit',
                        help='How many tracks to get if multiple(Max of 200). Defaults to 20')
    args = parser.parse_args()
    if args.SoundCloudURL == None:
        print('No arguments specified.')
        exit()
    else:
        download = SoundCloudDownload(args.SoundCloudURL, verbose=args.IsVerbose, tags=args.IncludeTags,
                                      artwork=args.IncludeArtwork, limit=args.GetTracksLimit)
        download.downloadAudio()
