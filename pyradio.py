#!/usr/bin/env python3

import argparse
import json
import requests
import signal
import sys
import time

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
        print(colors.YELLOW + "Station found in local database." + colors.ENDC)
    except KeyError:
        # Should we check TuneIn?
        if database:
            # No, user disabled it. Throw error.
            print(colors.RED + "Invalid station. Use --list to list all available stations." + colors.ENDC)
            sys.exit()

        print(colors.YELLOW + "Station not found in local database." + colors.ENDC)

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
    print(colors.BOLD + "Contacting station... " + colors.ENDC, end="")

    try:
        # Set stream to true so we only get the headers and dont load the body
        # otherwise it would hang and try to load the infinite stream
        with requests.get(station_url, stream=True) as r:
            # 200 is the default HTTP response code, if we get something else,
            # we can not play the stream (Debug : https://httpstat.us/)
            if r.status_code != 200:
                print(colors.RED + "Error!" + colors.ENDC)
                print(colors.RED + "Station unreachable: Site not working! Error " +
                    str(r.status_code) + "!" + colors.ENDC)

                sys.exit()

    except requests.ConnectionError:
        print(colors.RED + "Error!" + colors.ENDC)
        print(colors.RED + "Station unreachable: Unable to connect!" + colors.ENDC)
        sys.exit()

    print(colors.GREEN + "OK!" + colors.ENDC)

    # VLC player magic
    i = vlc.Instance("--quiet")
    m = i.media_new(station_url)
    p = m.player_new_from_media()
    p.audio_set_volume(vol)
    p.play()

    # Big print statement
    print(
            colors.GREEN + "\nYou are listening to: " + colors.ENDC +
            colors.BOLD + station + colors.ENDC +
            colors.GREEN + " at " + colors.ENDC +
            colors.UNDERLINE + station_url + colors.ENDC
    )

    oldTitle = None
    paused   = False

    while True:
        try:
            if not paused:
                # Get the song title from VLC
                m.parse()
                newTitle = m.get_meta(12)

                # If the title changed, update the message
                if newTitle != oldTitle:
                    oldTitle = newTitle
                    print(
                        "\r" + " "*100 + "\r" + # Clear the line
                        colors.GREEN + "Now playing: " + colors.ENDC +
                        colors.BOLD + newTitle + colors.ENDC, end=""
                    )

            time.sleep(1)

        # Ctrl+C pauses the playback.
        except KeyboardInterrupt:
            try:
                oldTitle = None       # We want to update the "Now playing message"
                paused   = not paused # Invert the paused state
                p.pause()

                # Only wait for a second Ctrl+C if we are pausing, not if we are unpausing
                if paused:
                    print(
                        "\r" + " "*100 + "\r" + # Clear the line
                        colors.YELLOW + "-> Press Ctrl+C again to exit!" + colors.ENDC, end=""
                    )

                    time.sleep(2)

                    # Now we no longer wait for a second Ctrl+C, we are just paused.
                    print(
                        "\r" + " "*100 + "\r" + # Clear the line
                        colors.YELLOW + "-> Playback paused! Ctrl+C to unpause!" + colors.ENDC, end=""
                    )

                # This is only really visible for stations which dont send song titles
                else:
                    print(
                        "\r" + " "*100 + "\r" + # Clear the line
                        colors.YELLOW + "-> Playback restarted!" + colors.ENDC, end=""
                    )

                continue

            # A second Ctrl+C ends the program.
            except KeyboardInterrupt:
                # To make your bash prompt not mess up :)  ~(>.<)~ a man of culture
                print("")
                p.stop()
                exit()


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
