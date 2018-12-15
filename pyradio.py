#!/usr/bin/env python3

import argparse
import json
import signal
import sys
import urllib.request

import vlc
import colorama


# Heh, ripped from the Blender build scripts
class colors:
    GREEN     = '\033[92m'
    RED       = '\033[91m'
    YELLOW    = '\033[93m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC      = '\033[0m'


def load_stations():
    try:
        with open("stations.json", "r") as f:
            stations = json.load(f)
            return stations
    except Exception:
        print(colors.RED + "Error loading stations.json. Have you forgot the comma?" + colors.ENDC)
        sys.exit()


def show_stations():
    stations = load_stations()

    print("Available stations:")
    print()
    for key, value in stations.items():

        # Formatted print
        print((colors.GREEN + "{0:16}" + colors.ENDC + " " + colors.UNDERLINE + "{1}" + colors.ENDC)
              .format(key, value))


def play_radio(station):
    stations = load_stations()

    try:
        station_url = stations[station]
    except KeyError:
        print(colors.RED + "Invalid station. Use --stations to list all available stations." + colors.ENDC)
        sys.exit()

    # Checking if the url is reachable. If not,
    # there might be a typo in the stations.json file
    try:
        r = urllib.request.urlopen(station_url)

        # 200 is the default HTTP response code
        # if we get something else, we can not play the stream
        if r.getcode() != 200:
            print(colors.RED + "Station not reachable: HTTP error!" + colors.ENDC)
            sys.exit()
    except urllib.error.URLError:
        print(colors.RED + "Station not reachable: URL error!" + colors.ENDC)
        sys.exit()

    p = vlc.MediaPlayer(station_url)
    p.play()

    # Big print statement
    print(
            colors.GREEN + "Now playing: " + colors.ENDC
            + colors.BOLD + station + colors.ENDC
            + colors.GREEN + " at " + colors.ENDC
            + colors.UNDERLINE + station_url + colors.ENDC
    )

    # Make all vlc errors yellow
    # This is why we dont use colorama "autoreset=True"
    print(colors.YELLOW)

    try:
        while True:
            # Keep program alive
            # Turns out looping the "pass" statement burns your performance, sorry!
            input()
            p.pause()

    except KeyboardInterrupt:
        # To make your bash prompt not mess up :)  ~(>.<)~ a man of culture
        print("")
        # Stop playback
        p.stop()


def main():
    # This disables CTRL+Z while the script is running (only on linux)
    if sys.platform != "win32":
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    # Initalize colorama
    colorama.init()

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
