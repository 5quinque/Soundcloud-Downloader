#!/usr/bin/python
import pip
import urllib
import tarfile
from subprocess import call
import os
import shutil

def install(package):
    pip.main(['install', package])

# Install soundcloud, requests with pip and ID3-PY with setup.py
if __name__ == '__main__':
    install('soundcloud')
    install('requests')
    if not os.path.exists('/tmp/dependencies'):
        os.makedirs('/tmp/dependencies')
    urllib.urlretrieve('http://id3-py.sourceforge.net/ID3.tar.gz', filename='/tmp/dependencies/ID3.tar.gz')
    tar = tarfile.open('/tmp/dependencies/ID3.tar.gz')
    tar.extractall(path='/tmp/dependencies')
    tar.close()
    os.chdir('/tmp/dependencies/id3-py-1.2')
    print call(['python', 'setup.py', 'install'])
    shutil.rmtree('/tmp/dependencies')
    print 'Done'
