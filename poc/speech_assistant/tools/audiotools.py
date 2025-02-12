import pyaudio
import datetime
import wave
from tools.logger import logger

def capture(seconds=20, stop_now=None, begin_callback=None):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = seconds
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    if begin_callback is not None:
        begin_callback()

    logger.debug('start')
    start = datetime.datetime.now()
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        if stop_now is not None and stop_now():
            break
        # TODO: Find a better way to handle this on MacOS
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    stop = datetime.datetime.now()
    logger.debug(f'stop - duration {stop-start}')

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
