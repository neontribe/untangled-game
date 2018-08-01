import pygame
import pygame.locals

from pyknon.genmidi import Midi
from pyknon.music import NoteSeq

class LevelMusic():
    def __init__(self, location):
        self.location = location

    def load_music(self):
        return pygame.mixer.music.load(self.location)

    # Play the music a given number of times.
    # -1 will play on repeat, 0 will play once and so on...
    @staticmethod
    def play_music(count):
        pygame.mixer.music.play(count)

    @staticmethod
    def play_music_repeat():
        pygame.mixer.music.play(-1)

    @staticmethod
    def stop_music():
        pygame.mixer.music.stop()

    # https://github.com/kroger/pyknon
    # e.g. TileMusic.create_music("D4 F#8 A Bb4", 90, 0, "Test")
    # Append given notes to a music file.
    @staticmethod
    def create_music(note_seq, given_tempo, given_track, song_name):
        notes = NoteSeq(note_seq)
        midi = Midi(1, tempo=given_tempo)
        midi.seq_notes(notes, track=given_track)
        file = ("assets\music\/" + song_name + ".mid")

        # Check if file exists
        if os.path.isfile(file):
            midi.write(file)
        else:
            print(song_name + ".mid Does not exist")
