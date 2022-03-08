# RPG Soundboard

This is a hardware based soundboard for RPG games.
It is based on the [Adafruit NeoTrellis M4](https://www.adafruit.com/product/4020)

## Configuration

The [sound_board.csv](soundboard/sound_board.csv) contains samples and [colorcodes](https://www.rapidtables.com/web/color/RGB_Color.html).

## Hacking

To connect to the console of the board, you need to `screen /dev/tty.usbmodem3201`

## Sounds

According to Adafruit, [mono sound files at 22KHz sample rate](https://learn.adafruit.com/microcontroller-compatible-audio-file-conversion) are best for the current crop of microcontrollers.

To convert soundfiles, we use `sox`

```
# Sample rate of 22 kHz (-r 22000),
# one channel (mono) (-c 1),
# 16 bits bit depth (-b 16).

sox in.wav -r 22000 -c 1 -b 16 out.wav
```

CircuitPython supports any MP3 file. Mono and stereo files from 32kbit/s to 128kbit/s work, with sample rates from 16kHz to 44.1kHz. The DAC output on the SAMD51 M4 is just 12-bit so there's not much point in using higher bitrates.

## Resources

### CircuitPython

* http://docs.circuitpython.org/projects/trellism4/en/latest/api.html
* https://circuitpython.readthedocs.io/en/latest/shared-bindings/audioio/index.html
* https://learn.adafruit.com/a-logger-for-circuitpython/using-a-logger

### Sound resources

* http://turbobard.com/
* https://freesound.org/
* https://wiki.roll20.net/Jukebox







