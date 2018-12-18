# pyradio
> Play your favorite radio station from the terminal

## Installation
```bash
# clone the repo
$ git clone https://github.com/sdushantha/pyradio

# install the requirements
$ pip3 install -r requirements.txt
```
This will clone the repository to your local PC and install the dependencies, python-vlc and colorama.

## Usage
```
$ python3 pyradio.py
usage: pyradio.py [-h] [-l] [-p STAT] [-v VOL]

Play your favorite radio station from the terminal

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list available radio stations
  -p STAT, --play STAT  play specified radio station
  -v VOL, --vol VOL     set playback volume (default: 100)
```
### Example
```bash
$ python3 pyradio.py -p NRJ
```

## Adding Radio Stations
To add more stations, add the URL pointing to the stream to the ```stations.json``` file.

Follow this format:
```
"station name": "link_to_stream"
```

## :scroll: License
MIT License

Copyright (c) 2018 Siddharth Dushantha
