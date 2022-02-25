# neotrellis

* the code in noise/7 produces a static white noise with a Neotrellis M4 whereas the code in noise/5 does not.
* 5 is using `adafruit-circuitpython-trellis_m4_express-en_US-5.1.0.uf2`
    * `adafruit-circuitpython-bundle-5.x-mpy-20201205`
* 7 is using `adafruit-circuitpython-trellis_m4_express-en_US-7.1.1.uf2`
    * `adafruit-circuitpython-bundle-7.x-mpy-20220127`


## development

```
screen /dev/tty.usbmodem3201
```

https://learn.adafruit.com/microcontroller-compatible-audio-file-conversion

>PCM 16-bit Mono WAV files at 22KHz sample rate, which is usually best for the current crop of microcontrollers which take WAV files and play them on a speaker.

https://unix.stackexchange.com/questions/274144/sox-convert-a-wav-file-with-required-properties-in-a-single-command

sox disturbence.wav -r 16000 -c 1 -b 16 disturbence_16000_mono_16bit.wav

gives within one command

Sample rate of 16 kHz (-r 16000),
one channel (mono) (-c 1),
16 bits bit depth (-b 16).

sox <infile> -r 22000 -c 1 -b 16 <outfile.wav>


## Docs
http://docs.circuitpython.org/projects/trellism4/en/latest/api.html
https://circuitpython.readthedocs.io/en/latest/shared-bindings/audioio/index.html
https://learn.adafruit.com/a-logger-for-circuitpython/using-a-logger

## Sounds

http://turbobard.com/
https://freesound.org/
https://wiki.roll20.net/Jukebox


CircuitPython supports any MP3 file you like. We've found that mono and stereo files from 32kbit/s to 128kbit/s work, with sample rates from 16kHz to 44.1kHz. The DAC output on the SAMD51 M4 is just 12-bit so there's not much point in using higher bitrates.


`find GDC -type f | head | xargs -I ./convert-mp3.sh`

# color_names
https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Colors/Color_picker_tool
https://www.rapidtables.com/web/color/RGB_Color.html