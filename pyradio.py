#!/usr/bin/env python3

import argparse
import json
import signal
import sys
import requests

import vlc
import colorama
import tunein


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

    print("Available stations:\n")
    for key, value in stations.items():

        # Formatted print
        print((colors.GREEN + "{0:16}" + colors.ENDC + colors.YELLOW + " @ " + colors.ENDC + colors.UNDERLINE + "{1}" + colors.ENDC)
              .format(key, value))


def play_radio(station, vol, database):
    stations = load_stations()

    try:
        # Check stations.json
        station_url = stations[station]
    except KeyError:
        print(colors.YELLOW + "Station not found in local database." + colors.ENDC)

        # Should we check TuneIn?
        if not database:
            station_id  = tunein.query_tunein(station)
            station_url = tunein.get_tunein_stream(station_id)
        else:
            # Throw error if search returned nothing
            print(colors.RED + "Invalid station. Use --list to list all available stations." + colors.ENDC)
            sys.exit()

        print(colors.BOLD + "Adding station to database... " + colors.ENDC, end="")

        # Add new station to local database
        stations[station] = station_url
        with open('stations.json', 'w') as f:
            json.dump(stations, f, indent=4, sort_keys=True)

        print(colors.GREEN + "OK!" + colors.ENDC)

    # Checking if the url is reachable. If not,
    # there might be a typo in the stations.json file
    try:
        # Set stream to true so we only get the headers and dont load the body
        # otherwise it would hang and try to load the infinite stream
        r = requests.get(station_url, stream=True)

        # 200 is the default HTTP response code
        # if we get something else, we can not play the stream
        if r.status_code != 200:
            print(colors.RED + "Station not reachable: Site not working: Error " +
                str(r.status_code) + "!" + colors.ENDC)

            sys.exit()
    except requests.ConnectionError:
        print(colors.RED + "Station not reachable: Unable to connect!" + colors.ENDC)
        sys.exit()

    p = vlc.MediaPlayer(station_url)
    p.audio_set_volume(vol)
    p.play()

    # Big print statement
    print(
            colors.GREEN + "\nNow playing: " + colors.ENDC
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
                        help="list all stations in local database")

    parser.add_argument("-d", "--database",
                        action="store_true",
                        help="only use local station database")

    parser.add_argument("-p", "--play", metavar="STAT",
                        help="play specified radio station")

    parser.add_argument("-v", "--vol", type=int, default=100,
                        help="set playback volume (default: 100)")

    args = parser.parse_args()

    # If argument is given show help
    if len(sys.argv) == 1:
        parser.print_help()

    if args.play:
        play_radio(str(args.play), args.vol, args.database)

    elif args.list:
        show_stations()

    sys.exit()


if __name__ == "__main__":
    main()
