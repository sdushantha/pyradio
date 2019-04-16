#!/usr/bin/env python3

import argparse
import json
import requests
import signal
import sys

import colorama
import vlc

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

    print("\nAvailable stations:\n")
    for key, value in stations.items():

        # Formatted print, dynamic for longest station name
        print((colors.GREEN + "{0:" + str(len(max(stations, key=len))) + "}"
             + colors.ENDC + colors.YELLOW + " @ " + colors.ENDC + colors.UNDERLINE + "{1}" + colors.ENDC)
             .format(key, value))


def play_radio(station, vol, database):
    stations = load_stations()

    try:
        # Check stations.json
        station_url = stations[station]
    except KeyError:
        print(colors.YELLOW + "Station not found in local database." + colors.ENDC)

        # Should we check TuneIn?
        if database:
            # No, user disabled it. Throw error.
            print(colors.RED + "Invalid station. Use --list to list all available stations." + colors.ENDC)
            sys.exit()

        station_data = tunein.query_data(station)
        station_url  = tunein.get_stream_link(station_data[1])
        station      = station_data[0] # Set station name as reported by TuneIn

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

    # This way, "station" can be a required positional argument,
    # but only if "--list" is not given. Also, we need to add these parameters if the user called "-h".
    if not(any(elem in sys.argv for elem in ["-l", "--list"])) or any(elem in sys.argv for elem in ["-h", "--help"]):
        parser.add_argument("-d", "--database",
                            action="store_true",
                            help="only use local station database")

        parser.add_argument("station",
                            type=str,
                            help="name of station to play, checked on TuneIn if unkown")

        parser.add_argument("volume",
                            type=int, default=100, nargs='?',
                            help="playback volume (default: 100)")

    args = parser.parse_args()

    if args.list:
        show_stations()

    elif args.station:
        play_radio(args.station, args.volume, args.database)

    sys.exit()


if __name__ == "__main__":
    main()
