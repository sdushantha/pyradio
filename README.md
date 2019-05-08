# pyradio
> Play your favorite radio station from the terminal

## Installation
```bash
# clone the repo
$ git clone https://github.com/sdushantha/pyradio

# change into the new directory
$ cd pyradio

# install the requirements
$ pip3 install -r requirements.txt
```
This will clone the repository to your local PC and install the dependencies, `colorama`, `python-vlc`, and `requests`.
Also, the [VLC media player](https://www.videolan.org/vlc/) must be installed.

## Usage
```
$ python3 pyradio.py -h
usage: pyradio.py [-h] [-p] [-l] [-d] [-s] [-c] [-b] station [volume]

Play your favorite radio station from the terminal

positional arguments:
  station         name of station to play, checked on TuneIn if unkown
  volume          playback volume (default: 100)

optional arguments:
  -h, --help      show this help message and exit
  -p, --print     print a list of all stations in the local database
  -l, --local     only use local station database for URL lookup
  -d, --download  save stream to files instead of playing
  -s, --split     do not split files saved with --download
  -c, --connect   treat the station argument as a direct URL
  -b, --block     block titles specified in blocked.json
```

### Example
```bash
$ python3 pyradio.py "NRJ"
```

## Adding Radio Stations
`pyradio.py` will search all unkown radio stations on [TuneIn](https://tunein.com/) and add them to the local database if anything is found.
Alternatively you also can add a station manually, to do so, add the URL pointing to the stream to the `stations.json` file.

Follow this format:
```
"station name": "link_to_stream"
```

## Downloading radio streams
`pyradio.py` is capable of downloading a stations stream instead of playing it. To use this function, pass the `-d` option.
This will create a folder named after the station and save the stream to multiple files, one for each track.
The splitting wont be perfect, because many stations send the track title shortly after the actual track started.
A list containing information on when a track was played can be found in `titles.txt`.

To disable the file splitting and instead save everything to a single file, pass the `-s` option.

## :scroll: License
MIT License

Copyright (c) 2018 Siddharth Dushantha, TeilzeitTaco
