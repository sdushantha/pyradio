#!/usr/bin/env python3

# TODO: Ad-blocking. How, you may ask? I suggest letting the user set a list of
# "banned" track titles which usally appear when ads are playing, and replacing
# them either with another radio stream or some pleasant elevator music (file/folder).
# As soon as we detect the track title changing again, we can switch back to the radio stream.
# Also, the same technique could be used to block unwanted "trending" songs!
# Progress: Done!

# TODO: Downloading of streams, splitting of the file in seperate music files per
# title and storing them in an seperate folder. Command line setting to disable
# file splitting.
# Progress: Beta, still kinda unhappy with this.

# TODO: Direct streaming: Let the user pass an URL and add it to the database,
# then play it.
# Progress: Done!

# TODO: Clean this mess!
# Progress: None

import argparse
import json
import requests
import signal
import sys
import time

import colorama
import vlc

import download
import tunein


# Heh, ripped from the Blender build scripts
class colors:
    GREEN     = '\033[92m'
    RED       = '\033[91m'
    YELLOW    = '\033[93m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC      = '\033[0m'


# Load the config file, config.json
def load_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            return config
    except Exception:
        print(colors.RED + "Error loading config.json. Have you forgot the comma?" + colors.ENDC)
        sys.exit()


# Outputs a nicly fomatted list of all stations.
def show_stations():
    stations = load_config()["Local Stations"]

    print("\nAvailable stations:\n")
    for key, value in stations.items():

        # Formatted print, dynamic for longest station name
        print((colors.GREEN + "{0:" + str(len(max(stations, key=len))) + "}"
             + colors.ENDC + colors.YELLOW + " @ " + colors.ENDC + colors.UNDERLINE + "{1}" + colors.ENDC)
             .format(key, value))

    sys.exit()


# Searches local database, query TuneIn if necessary, perform connection check
def initalize_radio(station_name, database):
    config = load_config()

    try:
        # Check config.json
        station_url = config["Local Stations"][station_name]
        print(colors.YELLOW + "Station found in local database." + colors.ENDC)
    except KeyError:
        # User may have disabled TuneIn search. If so, throw error.
        if database:
            print(colors.RED + "Invalid station. Use --print to list all available stations." + colors.ENDC)
            sys.exit()

        # This is our automatic link detection
        if station_name.lower().startswith("http"):
            print(colors.YELLOW + "Detected direct URL! " + colors.ENDC)
            station_url = station_name
        else:
            print(colors.YELLOW + "Station not found in local database." + colors.ENDC)

            station_data = tunein.query_data(station_name)
            station_url  = tunein.get_stream_link(station_data[1])
            station_name = station_data[0] # Set station name as reported by TuneIn

            print(colors.BOLD + "Adding station to database... " + colors.ENDC, end="")

            # Add new station to local database
            config["Local Stations"][station_name] = station_url
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4, sort_keys=True)

            print(colors.GREEN + "OK!" + colors.ENDC)

    # Checking if the url is reachable. If not,
    # there might be a typo in the config.json file
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
    return [station_name, station_url]


# Main radio logic
def play_station(station_name, station_url, volume):
    # TODO: MOVE THIS
    config = load_config()

    # VLC player magic
    instance = vlc.Instance("--quiet")

    # This are our player objects, which can play music.
    stream_player  = instance.media_player_new()
    adblock_player = instance.media_player_new()

    # This are our media objects, one for each player.
    stream_media  = instance.media_new(station_url)
    adblock_media = instance.media_new(config["Replace with"])

    stream_player.set_media(stream_media)
    adblock_player.set_media(adblock_media)

    stream_player.audio_set_volume(volume)
    adblock_player.audio_set_volume(volume)

    stream_player.play()

    # Big print statement
    if station_name.startswith("http"):
        print(
            colors.GREEN + "\nYou are listening to: " + colors.ENDC +
            colors.BOLD + station_name + colors.ENDC)
    else:
        print(
            colors.GREEN + "\nYou are listening to: " + colors.ENDC +
            colors.BOLD + station_name + colors.ENDC +
            colors.GREEN + " at " + colors.ENDC +
            colors.UNDERLINE + station_url + colors.ENDC)

    print(colors.YELLOW + "-> Playback started! Ctrl+C to pause!" + colors.ENDC, end="")

    # Length of the print above
    oldTitle = " "*37

    # States: 1 = playing, 2 = paused, 3 = blocking
    state = 1

    while True:
        try:
            if state == 1 or state == 3:
                # Get the song title from VLC
                stream_media.parse()
                newTitle = stream_media.get_meta(12)
                if not newTitle:
                    newTitle = ""

                # If the title changed, process
                if newTitle != oldTitle and newTitle != "":
                    if state == 3:
                        state = 1

                        adblock_player.stop()
                        stream_player.audio_set_volume(volume)

                    # Search if any of our blocked phrases are in the new title
                    for toCheck in config["Blocked Titles"]:
                        if toCheck.lower() in newTitle.lower():
                            state = 3

                    if state == 3:
                        # Sad fact: We cant .stop() the stream player,
                        # because it would stop us from getting new song titles.
                        # Instead, we have to silence it using .audio_set_volume(0).
                        # This may create additional overhead, but I am not aware of
                        # any better method to do this.
                        stream_player.audio_set_volume(0)
                        adblock_player.play()

                        print(
                            "\r" + " "*(13 + len(oldTitle))+ "\r" + # Clear the line
                            colors.YELLOW + "-> Blocked a title!" + colors.ENDC, end="")

                        oldTitle = newTitle
                        continue

                    print(
                        "\r" + " "*(13 + len(oldTitle))+ "\r" + # Clear the line
                        colors.GREEN + "Now playing: " + colors.ENDC +
                        colors.BOLD + newTitle + colors.ENDC, end="")
                    oldTitle = newTitle

            time.sleep(1.5)

        # A single Ctrl+C pauses the playback
        except KeyboardInterrupt:
            try:
                # If we are playing or blocking, we are now paused.
                # If we already are paused, we are now playing.
                if state == 1:
                    stream_player.pause()
                    state = 2
                elif state == 2:
                    state = 1
                elif state == 3:
                    adblock_player.pause()
                    state = 2

                # The pause handling
                if state == 2:
                    print(
                        "\r" + " "*(13 + len(oldTitle)) + "\r" + # Clear the line
                        colors.YELLOW + "-> Press Ctrl+C again to exit!" + colors.ENDC, end="")

                    # Here we wait for a second signal to end the program...
                    time.sleep(2)

                    # ...and apparently no signal was received. This means we are just paused.
                    print(
                        "\r" + " "*30 + "\r" +
                        colors.YELLOW + "-> Playback paused! Ctrl+C to unpause!" + colors.ENDC, end="")

                    continue

                # Here is the unpausing code:
                oldTitle = "" # We want to update the "Now playing" message

                # This is only really visible for stations which dont send song titles
                print(
                    "\r" + " "*38 + "\r" +
                    colors.YELLOW + "-> Playback restarted!" + colors.ENDC, end="")

                continue # ...with the "While True:" loop above!

            # A second Ctrl+C ends the program
            except KeyboardInterrupt:
                # To make your bash prompt not mess up :)  ~(>.<)~ a man of culture
                print("")

                # Stop playbock
                stream_player.stop()
                adblock_player.stop()

                sys.exit()


# Our main function. This runs at program start.
def main():
    # This disables Ctrl+Z while the script is running (only on Linux)
    if sys.platform != "win32":
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    # TODO: Look into "autoreset=True", rename arguments to better names!
    # Progress: Arguments

    # Initalize colorama
    colorama.init()

    parser = argparse.ArgumentParser(description="Play your favorite radio station from the terminal")

    parser.add_argument("-p", "--print",
                        action="store_true",
                        help="print a list of all stations in the local database")

    # This way, "station" can be a required positional argument,
    # but only if "--print" is not given. Also, we need to add these parameters if the user called "-h".
    if not(any(elem in sys.argv for elem in ["-p", "--print"])) or any(elem in sys.argv for elem in ["-h", "--help"]):
        parser.add_argument("-l", "--local",
                            action="store_true",
                            help="only use local station database for URL lookup")

        parser.add_argument("-d", "--download",
                            action="store_true",
                            help="save stream to files instead of playing")

        parser.add_argument("-s", "--split",
                            action="store_true",
                            help="do not split files saved with --download")

        parser.add_argument("station",
                            type=str,
                            help="name of station to play, checked on TuneIn if unknown")

        parser.add_argument("volume",
                            type=int, default=100, nargs='?',
                            help="playback volume (default: 100)")

    args = parser.parse_args()

    # Our actions are show_stations(), download_station(), and play_station().
    # We sys.exit() at the end of each of these.

    if args.print:
        show_stations()

    if args.station:
        station_data = initalize_radio(args.station, args.local)

        if args.download:
            download.download_station(station_data[0], station_data[1], args.split)

        play_station(station_data[0], station_data[1], args.volume)


if __name__ == "__main__":
    main()
