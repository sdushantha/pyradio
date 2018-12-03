# pyradio
> Play your favorite radio station from the terminal

## Installation
```bash
# clone the repo
$ git clone https://github.com/TeilzeitTaco/pyradio.git

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
  -l, --list            list available radio stations
  -p PLAY, --play PLAY  play specified radio station
```
### Example
```
$ python3 pyradio.py -p radi/u/
```

## Adding Radio Stations
To add more stations, add the url to the stream to the ```stations.json``` file.

Follow this format:
```
"station name": "link_to_stream"
```
### Tutorial: Obtaining TuneIn stream links
You can add [TuneIn](tunein.com) streams to the ```stations.json``` file.

* Navigate your browser to the TuneIn stream page
* Wait for advertisments to load/play
* Press ```F12``` or ```ctrl+shift+i``` to inspect the page (tested on Mozilla Firefox and Google Chrome)
* Press ```ctrl+f``` and search for ```<audio``` or ```jp_audio```
* Copy the link after ```src=```
* Press ```F12``` or ```ctrl+shift+i``` to leave inspect mode

Source: [Quora](https://www.quora.com/How-do-I-get-a-streaming-URL-for-Tunein)

*Note: I assume TuneIn stream URLs are temporary or device-specific. Please report any oddities you may find.*

## :scroll: License
MIT License

Copyright (c) 2018 Siddharth Dushantha

Modified by TeilzeitTaco
