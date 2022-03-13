"""
SoundBoard
"""


import time
import board
import audioio
import audiomp3
import adafruit_trellism4
import circuitpython_csv as csv
import gc
import random

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
        self.heartbeat_sample = None
        self.last_playing_time = time.time()
        self.heartbeat_time = 9.5 * 60
        self.deinit_while_not_playing = True
        self.mp3_decoder = None
        self.default_board = ''
        self.current_board = self.default_board
        self.board_ids = { self.current_board }
        self.default_color = BLACK

        self.init_samples()
        self.init_pixels()
        self.pixels._neopixel.brightness = 0.4

    def get_sample(self, board_idx, idx):
        if not board_idx in self.samples:
            self.samples[board_idx] = {}
        if not idx in self.samples[board_idx]:
            self.samples[board_idx][idx] = {}

        return self.samples[board_idx][idx]


    def init_samples(self, filename='sound_board.csv'):
        self.samples[self.default_board] = {} # default board
        for row in range(4):
            for col in range(8):
                self.samples[''][(row,col)] = {
                    'color': self.default_color,
                    'filename': ''
                }

        with open(filename, mode="r", encoding="utf-8") as f:
            csvreader = csv.reader(f, delimiter=',', quotechar='"')
            for row in csvreader:
                if not row[0].startswith('#'):
                    self.board_ids.add(row[0])

            f.seek(0)

            for row in csvreader:
                # log.debug(str(row))
                if not row[0].startswith('#'):
                    if len(row) < 5:
                        log.debug("Skipping: " + row.join())
                        continue
                    (board_idx, row, col, color, file, options) = (x.strip() for x in row[0:6])
                    # log.debug(str((board_idx,row,col,color,file,options)))
                    if row and col and color and file:
                        # offset row by 3 so that we can index with 0,0 in top left corner in config file
                        idx = (3-int(row),int(col))
                        entry = self.get_sample(board_idx, idx)
                        try:
                            entry['color'] = eval(color)
                        except (SyntaxError, NameError) as e:
                            log.debug(f'cant evaluate color {color}. Exception: "{e}"')
                            entry['color']= self.default_color

                        if file in self.board_ids:
                            entry['filename'] = file
                        else:
                            entry['filename'] = self.sample_prefix + file
                        if options == 'default':
                            self.heartbeat_sample = [board_idx, idx]
                        if board_idx == self.default_board:
                            for i in self.board_ids:
                                e = self.get_sample(i, idx)
                                e['color'] = entry['color']
                                e['filename'] = entry['filename']



    def init_pixels(self, board_idx = ''):
        self.pixels._neopixel.fill(0)
        for idx, sample in self.samples[board_idx].items():
            if 'color' in sample:
                self.pixels[idx] = sample['color']
            else:
                self.pixels[idx] = self.default_color

    def play(self, button_idx):
        if button_idx in self.samples[self.current_board]:
            sample = self.samples[self.current_board][button_idx]
        else:
            log.debug(f'{button_idx} not in board {self.current_board}')
            return

        # play the sample
        try:
            f = open(sample['filename'], 'rb')

            # wav = audiocore.WaveFile(f)
            if not self.mp3_decoder:
                # https://github.com/adafruit/circuitpython/issues/6111#issuecomment-1059209917
                log.debug('free mem %d', gc.mem_free())
                gc.collect()
                log.debug('free mem %d', gc.mem_free())
                self.mp3_decoder = audiomp3.MP3Decoder(f)
                log.debug('free mem %d', gc.mem_free())
            else:
                self.mp3_decoder.file = f

            if not self.audio:
                self.audio = audioio.AudioOut(left_channel=board.A1, right_channel=board.A0)

            # logging with audio info might crash with
            #   "RuntimeError: Internal audio buffer too small"
            # log.debug(sample['filename'] +
            #     ' - %d channels, %d bits per sample, %d Hz sample rate ' %
            #     (self.mp3_decoder.channel_count, self.mp3_decoder.bits_per_sample, self.mp3_decoder.sample_rate))
            log.debug(sample['filename'])

            self.audio.play(self.mp3_decoder)
            # reset color of current sample
            self.set_color(self.current_sample)
            # change color of button
            self.set_color(button_idx, WHITE)

            # set current sample
            self.current_sample = button_idx
        except OSError as e:
            if sample['filename'] in self.board_ids:
                # change board
                log.debug(f'change board to {sample['filename']}')
                self.current_board = sample['filename']
                self.init_pixels(self.current_board)
            else:
                # File not found! skip to next
                log.debug(str(e))
                pass
        except MemoryError as e:
            log.debug(f'failed to allocate memory - "{e}"')


    def set_color(self, button_idx, color=None):
        if not button_idx:
            log.debug('no button_idx in set_color?!')
            return

        if not color:
            if button_idx and button_idx in self.samples[self.current_board]:
                sample = self.samples[self.current_board][button_idx]
                color = sample['color']
            else:
                color = self.default_color

        self.pixels[button_idx] = color

    def check_playing(self):
        # FIXME: move to heartbeat method
        if not self.current_sample and self.heartbeat_sample and (time.time() - self.last_playing_time) > self.heartbeat_time:
            self.current_board = self.heartbeat_sample[0]
            self.play(self.heartbeat_sample[1])

        # shutdown audio to avoid static noise when not playing
        if self.deinit_while_not_playing and self.audio and not self.audio.playing:
            # https://github.com/adafruit/circuitpython/issues/4181#issuecomment-778324632
            log.debug("deinit audio")
            self.audio.deinit()
            self.audio = None

            # reset color
            self.set_color(self.current_sample)
            self.current_sample = None

            # set last playing time
            self.last_playing_time = time.time()

        if self.audio and self.audio.playing:
            # flash random color
            self.set_color(self.current_sample, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))


    def loop(self):
        current_press = set()

        while True:
            self.check_playing()

            # log.debug("tick...")
            # log.debug('free mem %d', gc.mem_free())
            pressed = set(self.board.pressed_keys)
            just_pressed = pressed - current_press
            # just_released = current_press - pressed

            for down in just_pressed:
                log.debug(str(down))
                self.play(down)

            time.sleep(0.1)
            current_press = pressed
