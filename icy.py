#!/usr/bin/env python3

import datetime
import re
import requests
import os


# We need to add this header so the server sends us metadata
headers     = {"Icy-MetaData": "1"}
station_url = "https://oe3shoutcast.sf.apa.at/"
start_time  = datetime.datetime.now()

if not os.path.exists("station"):
    os.mkdir("station")
os.chdir("station")

musicfile = open("stream.mp3", "wb")
textfile  = open("titles.txt", "w")


with requests.get(station_url, stream=True, headers=headers) as r:
    # The ICY format is as follows:
    # (music_size) bytes of raw music data | 1 byte of metadata_size | (metadata_size)*16 bytes of metadata
    # A good resource: https://thecodeartist.blogspot.com/2013/02/shoutcast-internet-radio-protocol.html

    music_size = int(r.headers["icy-metaint"]) # This is our music_size music data block size
    r.raw.read(music_size)                     # Throw away the first chunk, it creates errors.

    while True:
        # Get all the data!
        metadata_size = int.from_bytes(r.raw.read(1), byteorder="big")*16
        metadata      = r.raw.read(metadata_size)
        musicdata     = r.raw.read(music_size)

        # Flush the music data to our buffer file
        musicfile.write(musicdata)
        musicfile.flush()

        # Most servers only send metadata if the track changes, so we have to check.
        if metadata:
            # I am strongly confident this regex is optimal :D
            title  = re.match("StreamTitle='([^';]*)';", metadata.decode("utf-8"))

            # Build our info string containing timestamp, time offset in the music file,
            # and track name.
            buffer = (
                datetime.datetime.now().strftime("%H:%M:%S") +
                " (" + str(datetime.datetime.now() - start_time).split('.', 2)[0] + "): " +
                title[1] + "\n"
            )

            textfile.write(buffer)
            textfile.flush()
