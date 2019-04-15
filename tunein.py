#!/usr/bin/env python3

import json
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


# TuneIn constants
# Hellish link: I dont fully understand it, but it works.
TUNEIN_LINKSERVER = "https://opml.radiotime.com/Tune.ashx?id={}&render=json&listenId=1555086519&itemToken=BgUFAAEAAQABAAEAb28BKyAAAAEFAAA&formats=mp3,aac,ogg,flash,html,hls&type=station&serial=a79c8cb1-e983-4dff-a0e2-7b95771e8657&partnerId=RadioTime&version=3.14&itemUrlScheme=secure&reqAttempt=1"
TUNEIN_SEARCH     = "https://tunein.com/search/?query="
TUNEIN_FILTER     = "<h2 class=\"container-title__titleHeader___T_Nit\" data-testid=\"containerTitle\">Stations<\/h2>.{0,256}data-nexttitle=\"(.{0,64})\" data-nextguideitem=\"(.{0,64})\">"


def query_data(query):
    # Get station name and ID from TuneIn search page
    print(colors.BOLD + "Querying TuneIn... " + colors.ENDC, end='')

    # We need to filter the query to make it url conform
    query = query.replace(" ", "%20")
    query = query.replace("/", "%2F")
    query = query.replace(".", "")

    # Get html source code from website
    r = requests.get(TUNEIN_SEARCH + query)

    # Magic regex: only find elements of the stations list and get name and ID
    station_id = re.findall(TUNEIN_FILTER, r.text)

    # Search successful?
    if station_id:
        print(colors.GREEN + "OK!" + colors.ENDC)
        return station_id[0]

    # Throw error if unsuccessful
    print(colors.RED + "Error!" + colors.ENDC)
    print(colors.RED + "Unable to get TuneIn ID: Error finding query on TuneIn!" + colors.ENDC)
    sys.exit()


def get_stream_link(station_id):
    # Get stream url directly from the TuneIn servers
    # Bonus: Bypasses ads! :D
    print(colors.BOLD + "Getting stream url... " + colors.ENDC, end="")

    # Lets request the station server address from the TuneIn database
    r = requests.get(TUNEIN_LINKSERVER.format(station_id))
    respondedJson = json.loads(r.text)

    # The received JSON data may contain more than one entry in the body list,
    # for different audio qualities. The best quality is listed first,
    # so we use [0] to select the first one.
    if respondedJson["body"][0]["url"]:
        print(colors.GREEN + "OK!" + colors.ENDC)
        return respondedJson["body"][0]["url"]

    # Throw error
    print(colors.RED + "Error!" + colors.ENDC)
    print(colors.RED + "Unable to get TuneIn stream: Server error!" + colors.ENDC)
    sys.exit()
