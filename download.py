#!/usr/bin/env python3

# TODO: Clean this mess!
# Progress: None

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


# This function strips our string of any illegal chars.
def illegal_symbol_filter(filter_string):
    # Filter set for Windows filenames
    filter_set =  ["/", "\\", "<", ">", "|", ":", "*", "?", "\"", "\n"]

    # Reduced filter set for Linux
    if sys.platform != "win32":
        filter_set = ["/"]

    # Satanic filter
    for to_replace in filter_set:
        if to_replace in filter_string:
            filter_string = filter_string.replace(to_replace, "")
    return filter_string


# Check if a filename is legal and adjust it if otherwise.
def process_filename(filename):
    filename = illegal_symbol_filter(filename)

    # Some names may repeat, so we need to do some processing
    if os.path.exists(filename + ".mp3"):
        cycles = 2
        while os.path.exists(filename + " (" + str(cycles) + ").mp3"):
            cycles = cycles + 1
        filename = filename + " (" + str(cycles) + ")"
    return filename + ".mp3"


# A copy-paste of process_filename(), but without the .mp3
def process_foldername(foldername):
    foldername = illegal_symbol_filter(foldername)

    # Some names may repeat, so we need to do some processing
    if os.path.exists(foldername):
        cycles = 2
        while os.path.exists(foldername + " (" + str(cycles) + ")"):
            cycles = cycles + 1
        foldername = foldername + " (" + str(cycles) + ")"
    return foldername


# Save a station_name stream to MP3 files in a specific folder
def download_station(station_name, station_url, disable_splitting):
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
            # TODO: Change this so we can actually download stations which dont respond with metaint. Example: "pyradio.py radi/u/ -d"
            # Progress: None

            print(colors.RED + "Error!" + colors.ENDC)
            print(colors.RED + "Pyradio can not download this station!" + colors.ENDC)
            sys.exit()

        print(colors.GREEN + "OK!" + colors.ENDC)

        # Big print statement
        # If we got a direct URL, we dont print the "from" part. It would be redundant.
        if station_name.lower().startswith("http"):
            print(
                colors.GREEN + "\nNow downloading: " + colors.ENDC +
                colors.BOLD + station_name + colors.ENDC)
        else:
            print(
                colors.GREEN + "\nNow downloading: " + colors.ENDC +
                colors.BOLD + station_name + colors.ENDC +
                colors.GREEN + " from " + colors.ENDC +
                colors.UNDERLINE + station_url + colors.ENDC)

        print(colors.YELLOW + "-> Ctrl+C to exit!" + colors.ENDC, end="")

        # Create folder if it doesnt exist
        station_name = process_foldername(station_name)
        if not os.path.exists(station_name):
            os.mkdir(station_name)
        os.chdir(station_name)

        # Title list
        textfile = open("titles.txt", "w")

        if disable_splitting:
            musicfile = open("Unnamed Stream.mp3", "wb")

        # Throw away the first chunk, it creates errors.
        r.raw.read(music_size)

        try:
            while True:
                # Read raw bytes from the stream.
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

                        if disable_splitting:
                            display_name = newTitle
                        else:
                            # Open the new music file for the title
                            display_name = process_filename(newTitle)
                            musicfile    = open(display_name, "wb")

                        # Build our info string containing timestamp, time offset and filename
                        info = (
                            datetime.datetime.now().strftime("%H:%M:%S") +
                            " (" + str(datetime.datetime.now() - start_time).split('.', 2)[0] + "): " +
                            display_name + "\n")

                        textfile.write(info)
                        textfile.flush()

                # Flush the music data to our info file
                musicfile.write(musicdata)
                musicfile.flush()

        # User hit Ctrl+C, we need to exit
        except KeyboardInterrupt:
            print("")
            sys.exit()
