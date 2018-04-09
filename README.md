Used to download music files from SoundCloud.com even if the download button is not available

Just run the python script like:  
$ soundcloud-downloader.py http://soundcloud.com/user/songname  
or  
$ soundcloud-downloader.py http://soundcloud.com/user/sets/setname

Requirements
------------

Mutagen (for ID3 name tagging)
https://bitbucket.org/lazka/mutagen/downloads
OR `pip install mutagen`

Requests (for downloading SoundCloud pages)
pip install requests
