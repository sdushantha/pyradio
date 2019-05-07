#!/usr/bin/env python3

# TODO: Clean this mess!

import datetime
import os
import re
import requests
import sys


# Heh, ripped from the Blender build scripts
class colors:
    GREEN     = '\033[92m'
    RED       = '\033[91m'
    YELLOW    = '\033[93m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC      = '\033[0m'


# Check if a filename is legal and adjust it if otherwise.
def process_filename(filename):
    # Satanic filter
    for toReplace in ["/", "\\", "<", ">", "|", ":", "*", "?", "\"", "\n"]:
        if toReplace in filename:
            filename = filename.replace(toReplace, "")

    # Some names may repeat, so we need to do some processing
    if os.path.exists(filename + ".mp3"):
        cycles = 2
        while os.path.exists(filename + " (" + str(cycles) + ").mp3"):
            cycles = cycles + 1

        filename = filename + " (" + str(cycles) + ")"

    return filename + ".mp3"


# Save a station stream to MP3 files in a specific folder
def download_station(station, station_url, disable_splitting):
    # We need to add this header so the server sends us metadata
    headers    = {"icy-metadata": "1"}
    start_time = datetime.datetime.now()

    newTitle   = ""
    oldTitle   = ""

    print(colors.BOLD + "Getting inital metadata... " + colors.ENDC, end="")

    with requests.get(station_url, stream=True, headers=headers) as r:
        # The ICY format is as follows:
        # (music_size) bytes of raw music data | (1) byte of metadata_size | (metadata_size)*16 bytes of metadata
        # A good resource: https://thecodeartist.blogspot.com/2013/02/shoutcast-internet-radio-protocol.html

        try:
            # This is our music_size music data block size
            music_size = int(r.headers["icy-metaint"])
        except KeyError:
            print(colors.RED + "Error!" + colors.ENDC)
            print(colors.RED + "Pyradio cant download this station!" + colors.ENDC)
            sys.exit()

        print(colors.GREEN + "OK!" + colors.ENDC)

        # Big print statement
        print(
            colors.GREEN + "\nNow downloading: " + colors.ENDC +
            colors.BOLD + station + colors.ENDC +
            colors.GREEN + " from " + colors.ENDC +
            colors.UNDERLINE + station_url + colors.ENDC)

        # Create folder if it doesnt exist
        if not os.path.exists(station):
            os.mkdir(station)
        os.chdir(station)

        # Title list
        textfile = open("titles.txt", "w")

        if disable_splitting:
            musicfile = open("Unnamed Stream.mp3", "wb")

        # Throw away the first chunk, it creates errors.
        r.raw.read(music_size)

        try:
            while True:
                # Get all the data!
                metadata_size = int.from_bytes(r.raw.read(1), byteorder="big")*16
                metadata      = r.raw.read(metadata_size)
                musicdata     = r.raw.read(music_size)

                # Most servers only send metadata if the track changes, so we have to check.
                if metadata:
                    try:
                        # I am strongly confident this regex is optimal :D
                        newTitle = re.match("StreamTitle='([^;]*)';", metadata.decode("utf-8"))[1]
                    except TypeError:
                        pass

                    # Some servers send empty metadata. (Example: http://media-ice.musicradio.com/CapitalXTRANationalMP3)
                    if newTitle == "":
                        newTitle = "Unnamed Stream"

                    if newTitle != oldTitle:
                        oldTitle = newTitle

                        # Open the new music file for the title
                        if disable_splitting:
                            filename  = newTitle
                        else:
                            filename  = process_filename(newTitle)
                            musicfile = open(filename, "wb")

                        # Build our info string containing timestamp, time offset and filename
                        info = (
                            datetime.datetime.now().strftime("%H:%M:%S") +
                            " (" + str(datetime.datetime.now() - start_time).split('.', 2)[0] + "): " +
                            filename + "\n")

                        textfile.write(info)
                        textfile.flush()

                # Flush the music data to our info file
                musicfile.write(musicdata)
                musicfile.flush()

        # User hit Ctrl+C, we need to exit
        except KeyboardInterrupt:
            sys.exit()
