import requests

# We need to add this header so the server sends us metadata
headers     = {"Icy-MetaData": "1"}
station_url = "http://streams.bigfm.de/bigfm-deutschland-128-mp3?usid=0-0-H-M-D-02"
musicfile   = open("stream.mp3", 'wb')

with requests.get(station_url, stream=True, headers=headers) as r:
    # The ICY format is as follows:
    # (music_size) bytes raw music data | 1 byte metadata_size | (metadata_size) bytes metadata
    # A good resource: https://thecodeartist.blogspot.com/2013/02/shoutcast-internet-radio-protocol.html

    music_size = int(r.headers["icy-metaint"])
    r.raw.read(music_size) # Throw away the first chunk, it creates errors.

    while True:
        # Get all the data!
        metadata_size = int.from_bytes(r.raw.read(1), byteorder="big")*16
        metadata      = r.raw.read(metadata_size)
        musicdata     = r.raw.read(music_size)

        # Flush the music data to our buffer file
        musicfile.write(musicdata)

        if metadata:
            print(metadata.decode("utf-8"))
