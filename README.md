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
usage: pyradio.py [-h] [-l] [-d] [-s] [-o] station [volume]

Play your favorite radio station from the terminal

positional arguments:
  station         name of station to play, checked on TuneIn if unkown
  volume          playback volume (default: 100)

optional arguments:
  -h, --help      show this help message and exit
  -l, --list      list all stations in local database
  -d, --database  only use local station database
  -s, --save      save stream to files
  -o, --onefile   do not split files saved with --save
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
`pyradio.py` is capable of downloading a stations stream instead of playing it. To use this function, pass the `-s` option.
This will create a folder named after the station and save the stream to multiple files, one for each track.
The splitting wont be perfect, because many stations send the track title shortly after the actual track started.
A list containing information on when a track was played can be found in `titles.txt`.

To disable the file splitting and instead save everything to a single file, pass the `-o` option.

## :scroll: License
MIT License

Copyright (c) 2018 Siddharth Dushantha, TeilzeitTaco
