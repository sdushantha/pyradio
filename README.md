# pyradio
> Play your favorite radio station from the terminal

## Installation

```bash
# clone the repo
$ git clone https://github.com/sdushantha/pyradio.git

# install the requirements
$ pip3 install -r requirements.txt
```
## Usage
```
$ python3 pyradio.py
usage: pyradio.py [-h] [-l] [-p PLAY]

Play your favorite radio station from the terminal

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list of all available radio stations
  -p PLAY, --play PLAY  radio station you want to play
```
### Example
```bash
$ python3 pyradio.py -p NRJ
```

## Adding Radio Stations
To add more stations, add the url to the stream to ```stations.json``` file.

Follow this format:
```
"station name" : "link_to_stream"
```

## :scroll: License
MIT License

Copyright (c) 2018 Siddharth Dushantha
