# The Opus Codec for Arduino

Opus is a codec for interactive speech and audio transmission over the Internet.

Opus can handle a wide range of interactive audio applications, including
Voice over IP, videoconferencing, in-game  chat, and even remote live music
performances. It can scale from low bit-rate narrowband speech to very high
quality stereo music.

Opus, when coupled with an appropriate container format, is also suitable
for non-realtime  stored-file applications such as music distribution, game
soundtracks, portable music players, jukeboxes, and other applications that
have historically used high latency formats such as MP3, AAC, or Vorbis.

                    Opus is specified by IETF RFC 6716:
                    https://tools.ietf.org/html/rfc6716

The Opus format and this implementation of it are subject to the royalty-
free patent and copyright licenses specified in the file COPYING.

Opus packets are not self-delimiting, but are designed to be used inside a __container__ of some sort which supplies the decoder with each packet's length. Opus was originally specified for encapsulation in __Ogg containers__.

This project contains

- [the opus codec](https://opus-codec.org/)


## Installation in Arduino

You can download the library as zip and call include Library -> zip library. Or you can git clone this project into the Arduino libraries folder e.g. with

```
cd  ~/Documents/Arduino/libraries
git clone https://github.com/pschatzmann/codec-opus.git
```

You must also __install the related [codec-ogg](https://github.com/pschatzmann/codec-ogg) library__!

## Documentation

I recommend to use this library together with my [Arduino Audio Tools](https://github.com/pschatzmann/arduino-audio-tools). 
This is just one of many __codecs__ that I have collected so far: Further details can be found in the [Encoding and Decoding Wiki](https://github.com/pschatzmann/arduino-audio-tools/wiki/Encoding-and-Decoding-of-Audio) of the Audio Tools.


