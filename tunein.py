#!/usr/bin/env python3

import re
import requests
import json
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
TUNEIN_ROOT       = "https://tunein.com"
TUNEIN_SEARCH     = "/search/?query="

# Hellish link: I dont fully understand it, but it works.
TUNEIN_LINKSERVER = "https://opml.radiotime.com/Tune.ashx?id={}&render=json&listenId=1555086519&itemToken=BgUFAAEAAQABAAEAb28BKyAAAAEFAAA&formats=mp3,aac,ogg,flash,html,hls&type=station&serial=a79c8cb1-e983-4dff-a0e2-7b95771e8657&partnerId=RadioTime&version=3.14&itemUrlScheme=secure&reqAttempt=1"


def query_id(query):
    # Get TuneIn sub-link from the TuneIn search page.
    print(colors.BOLD + "Querying TuneIn... " + colors.ENDC, end='')

    # We need to filter the query to make it url conform
    query = query.replace(" ", "%20")
    query = query.replace("/", "%2F")
    query = query.replace(".", "")

    # Get html source code from website
    r = requests.get(TUNEIN_ROOT + TUNEIN_SEARCH + query)

    # Get the link with regex
    query      = query.replace("%2F", "")
    query      = query.replace("%20", "-")
    station_id = re.search("href=\"(.{0,64}" + query + ".{0,64})\/\">",
        r.text, flags=re.IGNORECASE)

    # Return or throw error
    if station_id:
        print(colors.GREEN + "OK!" + colors.ENDC)
        return station_id.group(1)

    # Throw error
    print(colors.RED + "Error!" + colors.ENDC)
    print(colors.RED + "Unable to get TuneIn ID: Error finding query on TuneIn!" + colors.ENDC)
    sys.exit()


def get_stream_link(station_id):
    # Get stream url directly from the TuneIn servers
    # Bonus: Bypasses ads! :D
    print(colors.BOLD + "Getting stream url... " + colors.ENDC, end="")

    # We only need the ID, not the whole sub-link
    m = re.search("-(s.{0,32}$)", station_id)
    if not m:
        print(colors.RED + "Error!" + colors.ENDC)
        print(colors.RED + "Unable to get TuneIn stream: Invalid parameters!" + colors.ENDC)
        sys.exit()

    # Lets request the station server address from the TuneIn database
    r = requests.get(TUNEIN_LINKSERVER.format(m.group(1)))
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
