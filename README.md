Used to download music files from SoundCloud.com even if the download button is not available
Just run the python script like:
$ soundcloud-downloader.py http://soundcloud.com/user/songname  
or  
$ soundcloud-downloader.py http://soundcloud.com/user/sets/setname

Usage: soundcloud-downloader.py [-d dir] [-o] Soundcloud_URL

Default download location is the directory of the script.

Optional argument '-d' allows you to download to a different different location:
Example:
Download to users Music directory in home directory:
Usage: soundcloud-downloader.py -o ~/Music http://soundcloud.com/user/songname

Optional argument '-o' overwrites existing files if downloading multiple times.  Default is to create a new file for each download.
If file exists, file is appended with '_(X)' where 'X' is an incremented integer.

Requirements
------------

ID3-PY (for name tagging)
http://id3-py.sourceforge.net/

Requests (for downloading SoundCloud pages)
pip install requests