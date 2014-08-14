SoundCloud Syncer 
-----------------

Used to sync a user's playlists with a local Music directory. The script is ran as follows:
$ soundcloud-syncer.py <SoundCloud Username> <Absolte Path to Local Music Directory> 

The first time you run this script, it will create the folder structure (create a directory
for each playlist) and also add a whitelist file in the local music directory. This whitelist
is more of a skip list as any playlist names listed in that file will not be synced. By default
all playlists are listed in that file after running the script the first time. Remove desired
playlists from that file and run the script again. 


SoundCloud Downloader 
---------------------

Used to download music files from SoundCloud.com even if the download button is not available
Just run the python script like:  
$ soundcloud-downloader.py http://soundcloud.com/user/songname  
or  
$ soundcloud-downloader.py http://soundcloud.com/user/sets/setname

Requirements
------------

ID3-PY (for name tagging)
http://id3-py.sourceforge.net/

Requests (for downloading SoundCloud pages)
pip install requests
