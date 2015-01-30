Used to download music files from SoundCloud.com even if the download button is not available.
Just run the python script like:
------------
$ soundcloud-downloader.py --d http://soundcloud.com/user/songname  
or  
$ soundcloud-downloader.py --d http://soundcloud.com/user/sets/setname  
or  
$ soundcloud-downloader.py --d http://soundcloud.com/stream 
Note: 
Downloading from stream requires you use a password and username.
Help:
------------
$ soundcloud-downloader.py -h for more options

Requirements:
------------
(Optional)mutagen (for name tagging)  
https://bitbucket.org/lazka/mutagen  
pip install mutagen  
  
(Optional)soundcloud-python  
https://github.com/soundcloud/soundcloud-python  
pip install soundcloud  
NOTE** for now please download and install from the link as they haven't sent the current update available on pip  
  
Requests (for downloading SoundCloud pages)  
pip install requests  
