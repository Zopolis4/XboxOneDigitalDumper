#!/usr/bin/env python3
import argparse
import codecs
import ctypes
import os
import requests
import zlib
import hashlib as hash
from clint.textui import progress
from urlextract import URLExtract

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='tmp', nargs='+')
    args = parser.parse_args()
    for file in args.input:
        handle_file(file)

def handle_file(file):
    extractor = URLExtract()
    with codecs.open(file, 'r', 'utf-16-le') as file:
        data = file.read()
        split = data.replace('[XBL:]\\', ' ')
        urls = extractor.find_urls(split)
        handle_url(urls[0].rstrip('\x00'))

def handle_url(url):
    filepath = os.path.basename(url)
    r = requests.get(url, stream = True)
    with open(filepath, "wb") as download:
        total_length = int(r.headers.get('content-length'))
        for ch in progress.bar(r.iter_content(chunk_size = 2391975), expected_size=(total_length/1024) + 1):
            if ch:
                download.write(ch)
    print_filename(filepath, url)

def print_filename(filepath, url):
    print("Filename:", filepath)
    print_filesize(filepath, url)

def print_filesize(filepath, url):
    print("Filesize:", os.path.getsize(filepath))
    print_url(filepath, url)

def print_url(filepath, url):
    print("URL:", url)
    hash_file(filepath)

def hash_file(filepath):
    md5 = hash.md5()
    sha1 = hash.sha1()
    with open(filepath, 'rb') as input:
        buffer = input.read(65536)
        crcvalue = 0
        while len(buffer) > 0:
            crcvalue = zlib.crc32(buffer, crcvalue)
            md5.update(buffer)
            sha1.update(buffer)
            buffer = input.read(65536)
    print("CRC32:", (format(crcvalue & 0xFFFFFFFF, '08x')))
    print("MD5:", md5.hexdigest())
    print("SHA1:", sha1.hexdigest())

if __name__ == '__main__':
    main()