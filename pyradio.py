#!/usr/bin/env python3

import argparse
import json
import signal
import sys
import urllib.request
import vlc


# Heh, ripped from the Blender build scripts
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def show_stations():
    with open("stations.json", "r") as f:
        stations = json.load(f)

    print("Available stations:")
    print()
    for key, value in stations.items():

        # Formatted print
        print((colors.OKGREEN + "{0:16}" + colors.ENDC + " " + colors.UNDERLINE + "{1}" + colors.ENDC)
              .format(key, value))


def play_radio(station):
    with open("stations.json", "r") as f:
        stations = json.load(f)

    try:
        station_url = stations[station]
    except KeyError:
        print(colors.FAIL + "Invalid station. use --stations to list all available stations" + colors.ENDC)
        sys.exit()

    # Checking if the url is reachable. If not,
    # there might be a typo in the stations.json file
    try:
        r = urllib.request.urlopen(station_url)

        # 200 is the default HTTP response code
        # if we get something else, we can not play the stream
        if r.getcode() != 200:
            print(colors.FAIL + "Station not reachable: HTTP error!" + colors.ENDC)
            sys.exit()
    except urllib.error.URLError:
        print(colors.FAIL + "Station not reachable: URL error!" + colors.ENDC)
        sys.exit()

    p = vlc.MediaPlayer(station_url)
    p.play()

    # Big print statement
    print(
            colors.OKGREEN + "Now playing: " + colors.ENDC
            + colors.BOLD + station + colors.ENDC
            + colors.OKGREEN + " at " + colors.ENDC
            + colors.UNDERLINE + station_url + colors.ENDC
    )

    try:
        while True:
            # Keep program alive
            pass

    except KeyboardInterrupt:
        # To make your bash prompt not mess up :)  ~(>.<)~ a man of culture
        print("")
        # Stop playback
        p.stop()


def main():
    # This disables CTRL+Z while the script is running
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    parser = argparse.ArgumentParser(description="Play your favorite radio station from the terminal")

    parser.add_argument("-l", "--list",
                        action="store_true",
                        help="list available radio stations")

    parser.add_argument("-p", "--play",
                        help="play specified radio station")

    args = parser.parse_args()

    # If argument is given show help
    if len(sys.argv) == 1:
        parser.print_help()

    if args.play:
        play_radio(str(args.play))

    elif args.list:
        show_stations()

    sys.exit()


if __name__ == "__main__":
    main()
