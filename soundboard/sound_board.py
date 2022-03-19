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
import sys
import os
import microcontroller

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

E_COLOR = 0x0
E_FILE = 0x1


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
        self.board_ids = set()
        self.default_color = BLACK

        self.play_file('boot.mp3')

        self.init_samples()
        self.current_board = self.board_ids.copy().pop()
        self.init_pixels(self.current_board)
        self.pixels._neopixel.brightness = 0.4



    def get_sample(self, board_idx, idx):
        if not board_idx in self.samples:
            self.samples[board_idx] = {}
        if not idx in self.samples[board_idx]:
            self.samples[board_idx][idx] = {}

        return self.samples[board_idx][idx]


    def init_samples(self, filename='sound_board.csv'):
        with open(filename, mode="r", encoding="utf-8") as f:
            csvreader = csv.reader(f, delimiter=',', quotechar='"')
            for row in csvreader:
                board_id = row[0].strip()
                if not board_id.startswith('#') and board_id:
                    self.board_ids.add(row[0])

            f.seek(0)

            header = None
            required_keys = {'board','row','column','color','file','option'}
            for row in csvreader:
                # log.debug(str(row))
                if not header:
                    header = row
                    missing_keys = required_keys - set(header)
                    if missing_keys:
                        log.debug(f'Missing keys {missing_keys} in CSV')
                        sys.exit(1)
                    continue

                if row[0].startswith('#'):
                    log.debug(f'Skipping comment row {row}')
                    continue

                if len(row) < len(header):
                    log.debug(f'Skipping because too few columns in row {row}')
                    continue

                # map row
                e = {}; i = 0
                for k in header:
                    e[k] = row[i].strip()
                    i = i + 1

                board_idx = e['board']
                file = e['file']
                color = e['color']
                row = e['row']
                column = e['column']
                option = e['option']

                sample = {}

                # offset row by 3 so that we can index with 0,0 in top left corner in config file
                try:
                    idx = (3-int(row),int(column))
                except (ValueError) as ex:
                    log.debug(f'cant evaluate row/column "{row}"/"{column}". Exception: "{ex}"')


                try:
                    if color == 'RANDOM':
                        sample[E_COLOR] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    else:
                        sample[E_COLOR] = eval(color)
                except (SyntaxError, NameError) as ex:
                    log.debug(f'cant evaluate color {color}. Exception: "{ex}"')
                    continue

                if file in self.board_ids:
                    # it's a pointer to a board
                    sample[E_FILE] = file
                else:
                    filename = self.sample_prefix + file
                    try:
                        os.stat(filename)
                        sample[E_FILE] = filename
                        if option == 'default':
                            self.heartbeat_sample = [board_idx, idx]
                    except OSError as e:
                        # File not found!
                        log.debug(f'file does not exist {file}')
                        continue

                if board_idx:
                    s = self.get_sample(board_idx, idx)
                    s[E_COLOR] = sample[E_COLOR]
                    s[E_FILE] = sample[E_FILE]
                else:
                    # empty board_id -> put it on every board
                    for i in self.board_ids:
                        s = self.get_sample(i, idx)
                        s[E_COLOR] = sample[E_COLOR]
                        s[E_FILE] = sample[E_FILE]



    def init_pixels(self, board_idx):
        self.pixels._neopixel.fill(0)
        for idx, sample in self.samples[board_idx].items():
            if E_COLOR in sample:
                self.pixels[idx] = sample[E_COLOR]
            else:
                self.pixels[idx] = self.default_color

    def play_file(self, filename):
        try:
            f = open(filename, 'rb')

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
            # log.debug(sample[E_FILE] +
            #     ' - %d channels, %d bits per sample, %d Hz sample rate ' %
            #     (self.mp3_decoder.channel_count, self.mp3_decoder.bits_per_sample, self.mp3_decoder.sample_rate))
            log.debug(f'playing {filename}')

            self.audio.play(self.mp3_decoder)
        except OSError as e:
            # File not found!
            log.debug(str(e))
        except MemoryError as e:
            log.debug(f'failed to allocate memory - "{e}"')


    def play(self, button_idx):
        if button_idx in self.samples[self.current_board]:
            sample = self.samples[self.current_board][button_idx]
        else:
            log.debug(f'{button_idx} not in board {self.current_board}')
            return

        filename = sample[E_FILE]

        # change board
        if filename in self.board_ids:
            log.debug(f'change board to {filename}')
            self.current_board = filename
            self.init_pixels(self.current_board)
            return


        # play the sample
        self.play_file(filename)

        # reset color of current sample
        if self.current_sample:
            self.set_color(self.current_sample)

        # # change color of button
        # self.set_color(button_idx, WHITE)

        # self.pixels._neopixel.brightness = 0.4

        # set current sample
        self.current_sample = button_idx


    def set_color(self, button_idx, color=None):
        if not button_idx:
            log.debug('no button_idx in set_color?!')
            raise

        if not color:
            if button_idx and button_idx in self.samples[self.current_board]:
                sample = self.samples[self.current_board][button_idx]
                color = sample[E_COLOR]
            else:
                color = self.default_color

        self.pixels[button_idx] = color

    def stop_playing(self):
        if self.audio and self.audio.playing:
            log.debug('stop_playing')
            self.audio.stop()

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
            if self.current_sample:
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

            # like ctr-alt-del 
            # press top-right / top-left keys at once to reset
            if pressed and len(pressed) > 1:
                print(pressed)
                if pressed == {(3, 7), (3, 0)}:
                    microcontroller.reset()

            just_pressed = pressed - current_press
            # just_released = current_press - pressed

            for down in just_pressed:
                log.debug(f'press {down}')
                if down == self.current_sample:
                    self.stop_playing()
                else:
                    self.play(down)

            time.sleep(0.1)
            current_press = pressed

            # mem = []
            # if True:
            #     log.debug('free mem %d', gc.mem_free())
            #     for i in range(5):
            #         mem.append([0]*256)
