"""
SoundBoard
"""


import time
import board
import audioio
import audiocore
import adafruit_trellism4

RED = 0xFF0000
MAROON = 0x800000
ORANGE = 0xFF8000
YELLOW = 0xFFFF00
OLIVE = 0x808000
GREEN = 0x008000
AQUA = 0x00FFFF
TEAL = 0x008080
BLUE = 0x0000FF
NAVY = 0x000080
PURPLE = 0x800080
PINK = 0xFF0080
WHITE = 0xFFFFFF
BLACK = 0x000000

import adafruit_logging as logging
log = logging.getLogger('test')
log.setLevel(logging.DEBUG)

class SoundBoard:
    def __init__(self, board=adafruit_trellism4.TrellisM4Express(rotation=90)):
        self.board = board
        self.pixels = board.pixels
        self.audio = None
        self.samples = {}
        self.current_sample = None
        self.sample_prefix = 'samples/'

        self.init_samples()
        self.init_pixels()                
        self.pixels._neopixel.brightness = 0.2


    def init_samples(self, filename='soundboard.txt'):
        for row in range(4):
            for col in range(8):
                self.samples[(row,col)] = {
                    'color': BLACK,
                    'filename': ''
                }


        with open(filename, 'r') as f:
            for line in f:
                if line[0] != '#':
                    (row,col,color,file) = [x.strip() for x in line.split(',')]
                    log.debug(str((row,col,color,file)))
                    # offset row by 3 so that we can index with 0,0 in top left corner in config file
                    idx = (3-int(row),int(col))
                    entry = self.samples[idx]
                    entry['color'] = eval(color)
                    entry['filename'] = self.sample_prefix + file

    def init_pixels(self):
        self.pixels._neopixel.fill(0)
        for idx, sample in self.samples.items():
            print(idx)
            print(sample)
            self.pixels[idx] = sample['color']

    def play(self, button_idx):
        sample = self.samples[button_idx]

        if not self.audio:
            self.audio = audioio.AudioOut(board.A1)

        
        # play the sample
        try:
            f = open(sample['filename'], 'rb')
            wav = audiocore.WaveFile(f)
            log.debug(sample['filename'] +
                '%d channels, %d bits per sample, %d Hz sample rate ' %
                (wav.channel_count, wav.bits_per_sample, wav.sample_rate))

            self.audio.play(wav)
            # change color of button
            self.set_color(self.current_sample)
            self.set_color(button_idx, WHITE)

            # set current sample
            self.current_sample = button_idx
                
        except OSError as e:
            # File not found! skip to next
            log.debug(str(e))
            pass


    def set_color(self, button_idx, color=None):
        if button_idx:
            sample = self.samples[button_idx]
            if not color:
                color = sample['color']
            self.pixels[button_idx] = color

    def check_playing(self):
        # shutdown audio to avoid static noise when not playing
        if self.audio and not self.audio.playing:
            self.audio.deinit()
            self.audio = None

            # reset color 
            self.set_color(self.current_sample)
            self.current_sample = None


    def loop(self):
        current_press = set()
        while True:
            self.check_playing()

            # log.debug("tick...")
            pressed = set(self.board.pressed_keys)
            just_pressed = pressed - current_press
            # just_released = current_press - pressed

            for down in just_pressed:
                log.debug(str(down))
                self.play(down)
            
            time.sleep(0.1)
            current_press = pressed






