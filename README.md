# pyradio
> Play your favorite radio station from the terminal

## Installation
```bash
# clone the repo
$ git clone https://github.com/TeilzeitTaco/pyradio.git

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
```
$ python3 pyradio.py -p radi/u/
```
This example should play the [radi/u/](http://radio.dangeru.us/) stream.

## Adding Radio Stations
To add more stations, add the URL pointing to the stream to the ```stations.json``` file.

Follow this format:
```
"station name": "link_to_stream"
```
### Tutorial: Obtaining TuneIn stream links
You can add [TuneIn](https://tunein.com/) streams to the ```stations.json``` file.

* Navigate your browser to the TuneIn stream page
* Wait for advertisements to load/stop playing
* Press ```F12``` or ```ctrl+shift+i``` to inspect the page (tested on Mozilla Firefox and Google Chrome)
* Press ```ctrl+f``` and search for ```audio``` or ```jp_audio```
* Copy the link after ```src=```
* Press ```F12``` or ```ctrl+shift+i``` again to leave inspect mode
* Add the link to the ```stations.json``` file

Source: [Quora](https://www.quora.com/How-do-I-get-a-streaming-URL-for-Tunein)

*Note: I assume that some TuneIn stream URLs are temporary or device-specific. Please report any oddities you may find.*

## :scroll: License
MIT License

Copyright (c) 2018 Siddharth Dushantha

Modified by TeilzeitTaco for Windows compatibility, styling and other minor tweaks
