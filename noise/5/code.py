import time
import board
import audioio
import audiomixer
import adafruit_trellism4

# Our keypad + neopixel driver
trellis = adafruit_trellism4.TrellisM4Express(rotation=90)
audio = audioio.AudioOut(board.A1, quiescent_value=50)
mixer = audiomixer.Mixer()
audio.play(mixer)

while True:
    time.sleep(0.5)
    print("tick..")
    audio.pause()
