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
usage: pyradio.py [-h] [-p] [-l] [-d] [-s] station [volume]

Play your favorite radio station from the terminal

positional arguments:
  station         name of station to play, checked on TuneIn if unknown
  volume          playback volume (default: 100)

optional arguments:
  -h, --help      show this help message and exit
  -p, --print     print a list of all stations in the local database
  -l, --local     only use local station database for URL lookup
  -d, --download  save stream to files instead of playing
  -s, --split     do not split files saved with --download
```

### Example
```bash
$ python3 pyradio.py "NRJ"
```

## Adding radio stations
`pyradio.py` will search all unknown radio stations on [TuneIn](https://tunein.com/) and add them to the local database if anything is found.
Alternatively you also can add a station manually, to do so, add the URL pointing to the stream to the `config.json` file, more specific the `Local Stations` list.
If you instead just quickly want to test a new station, just pass the stream URL instead of the station name to `pyradio.py`.

Follow this format:
```
"station name": "link_to_stream"
```

## Blocking radio stations
`pyradio.py` can block user-specified titles and replace them with either another radio station or a local music file.
To use this feature, add the title or artist name to the `Blocked titles` list in the `config.json` file and set the replacement with `Replace with`.

Follow this format for the blocked title list:
```
"name fragment to block"
```

And this format for the `Replace with` entry:
```
"Replace with": "filename.mp3 or link_to_stream"
```

## Downloading radio streams
`pyradio.py` is capable of downloading a stations stream instead of playing it. To use this function, pass the `-d` option.
This will create a folder named after the station and save the stream to multiple files, one for each track.
The splitting wont be perfect, because many stations send the track title shortly after the actual track started.
A list containing information on when a track was played can be found in `titles.txt`.

To disable the file splitting and instead save everything to a single file, pass the `-s` option.

## License
MIT License

Copyright (c) 2018 Siddharth Dushantha, TeilzeitTaco
