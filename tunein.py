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
    query = query.replace("\\", "%5C")
    query = query.replace(".", "")

    # Get html source code from website
    with requests.get(TUNEIN_SEARCH + query) as r:
        # Magic regex: only find elements of the stations list and get name and ID
        station_id = re.findall(TUNEIN_FILTER, r.text)

    # Search successful?
    if station_id:
        print(colors.GREEN + "OK!" + colors.ENDC)
        return station_id[0]

    # Throw error if unsuccessful
    print(colors.RED + "Error!" + colors.ENDC)
    print(colors.RED + "Unable to get TuneIn ID: Search returned nothing!" + colors.ENDC)
    sys.exit()


def get_stream_link(station_id):
    # Get stream url directly from the TuneIn servers. Bonus: Bypasses ads! :D
    print(colors.BOLD + "Getting stream URL... " + colors.ENDC, end="")

    # Lets request the station server address from the TuneIn database.
    with requests.get(TUNEIN_LINKSERVER.format(station_id)) as r:
        try:
            respondedJson = json.loads(r.text)
        except Exception:
            # This really should not happen.
            print(colors.RED + "Error!" + colors.ENDC)
            print(colors.RED + "Server error: Malformed data!" + colors.ENDC)
            sys.exit()

    # Request successful?
    if respondedJson["head"]["status"] != "200":
        print(colors.RED + "Error!" + colors.ENDC)
        print(colors.RED + "Unable to get TuneIn stream: Server error!" + colors.ENDC)
        sys.exit()

    # Some stations dont have the direct stream url listed on the TuneIn linkserver.
    # This is indicated by the "is_direct" flag. If it is the direct link, we return it,
    # if not, we need to look at the second stage link. Example: "pyradio.py "WBER""

    # Station link is already in JSON, just return it.
    if respondedJson["body"][0]["is_direct"]:
        # The received JSON data may contain more than one entry in the body list,
        # for different audio qualities. The best quality is listed first,
        # so we use "[0]" to select and return it.
        print(colors.GREEN + "OK!" + colors.ENDC)
        return respondedJson["body"][0]["url"]

    # Station link is not in this JSON, search for more.
    print(colors.GREEN + "OK!" + colors.ENDC)
    print(colors.BOLD + "Second stage resolving... " + colors.ENDC, end="")

    # Get new JSON data from the secondary server
    with requests.get(respondedJson["body"][0]["url"]) as r:
        try:
            respondedJson = json.loads(r.text)
        except Exception:
            print(colors.RED + "Error!" + colors.ENDC)
            print(colors.RED + "Server error: Malformed data!" + colors.ENDC)
            sys.exit()

    print(colors.GREEN + "OK!" + colors.ENDC)
    return respondedJson["Streams"][0]["Url"]
