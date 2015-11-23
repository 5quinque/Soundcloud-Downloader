Used to download music files from SoundCloud.com even if the download button is not available.<br>
**NOTE**: This script requires an API Key from soundcloud (http://soundcloud.com/you/apps)
Just run the python script like:
------------
$ soundcloud-downloader.py --d "http://soundcloud.com/user/songname"  
or  
$ soundcloud-downloader.py --d "http://soundcloud.com/user/sets/setname"  
or  
$ soundcloud-downloader.py --d "http://soundcloud.com/stream" --u "user_email" --p "password"  
**NOTE**:<br>
Downloading from stream requires that you use a password and username.  

Arguments:
------------
*   -v for verbose
*   -t for id3 tags(requires mutagen)
*   -a for artwork(requires mutagen and -t argument)

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
  
Requests (for downloading SoundCloud pages)  
pip install requests  
