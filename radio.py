import vlc
import json
import argparse
import signal
import sys
import urllib.request


def show_all_stations():
	with open("stations.json", "r") as f:
		stations = json.load(f)

	for key in stations.keys():
		print(key)


def play_radio(station):
	with open("stations.json", "r") as f:
		stations = json.load(f)

	# I know this takes some time to start. First it has to 
	# Check the url and if it works, it takes time get a 
	# response. The it takes around 10 sec to get get the audio
	# from the url. I need to find a way to make this faster.

	try:
		station_url = stations[station]
	except KeyError:
		print("Invalid station. --stations to list all of the available stations")
		sys.exit()

	# Checking if the url is reachable. If not,
	# there might be a typo in the stations.json file
	try:
	    r = urllib.request.urlopen(station_url)

	    if r.getcode() != 200:
		    print("Station not reachable")
		    sys.exit()
	except urllib.error.URLError:
		print("Station not reachable")
		sys.exit()

	    
	p = vlc.MediaPlayer(station_url)
	# Takes some time to start the stream
	print("Radio will start playing in 10 sec")
	p.play()

	running = True

	# Dumb trick to keep the script running
	try:
		while running:
		    input("")

	except KeyboardInterrupt:
		# To make your bash prompt not mess up :)
		print("")
		sys.exit()


def main():
	# This disables CTRL+Z while the script is running
	signal.signal(signal.SIGTSTP, signal.SIG_IGN)

	parser = argparse.ArgumentParser(description = "Play your favorite radio station from the terminal")

	parser.add_argument("-l", "--list",
		action="store_true",
		help="list of all available radio stations")

	parser.add_argument("-p", "--play",
	    help="radio station you want to play")

	args = parser.parse_args()


    # if argument is given then show help
	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit()

	if args.play:
		play_radio(str(args.play))

	elif args.list:
		show_all_stations()
		sys.exit()


if __name__=="__main__":
	main()