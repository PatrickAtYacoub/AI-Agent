
from pydub import AudioSegment
from pydub.playback import play
import subprocess
from tools.logger import logger

def playsound(file):
    # file_name = os.path.join('C:\\Windows', 'Media', file)
    song = AudioSegment.from_wav(f"./data/{file}")
    logger.debug(f'playing {file} with {song.dBFS} dB')
    play(song)
    pass


def beep():
    playsound('chord.wav')


def ok_beep():
    playsound('ding.wav')


def bad_beep():
    playsound('Windows Error.wav')


def to_mp3():
    INPUT_FILE = "output.wav"
    OUTPUT_FILE = "output.mp3"

    with open(INPUT_FILE, 'rb') as f:
        raw_pcm = f.read()

    lame = subprocess.Popen(["lame", "-", OUTPUT_FILE], stdin=subprocess.PIPE)
    lame.communicate(input=raw_pcm)

    pass
