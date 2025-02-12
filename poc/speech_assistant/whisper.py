import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))

parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
lib_dir = os.path.join(parent_dir, 'lib')
sys.path.append(lib_dir)
poc_dir = os.path.join(parent_dir, 'poc')
sys.path.append(poc_dir)



from pynput.keyboard import Listener
import time
from lib.container_tools import as_list
from lib.path_tools import path_get
from tools.propagating_thread import PropagatingThread
from tools.sound_tools import *
from tools.dispatcher import CommandDispatcher, dispatch_response, halt_requested
from tools.logger import logger
from tools.audiotools import capture
from lib.apicall import api
from poc.langchain.agents import agent



def to_text():
    logger.debug('To Text Handler')
    # transcript = send_whisper_request(lease, 'output.wav')
    transcript = api.send_request('whisper', 'output.wav')
    logger.info(str(transcript))
    return transcript


def watch_keys(keydown_functions=None, keyup_functions=None):

    def prepare_handler():
        def run_handler():
            nonlocal handler_prepared
            time.sleep(0.35)
            handler = get_handler_for_key_press(keydown_functions)
            logger.debug(f'handler: {handler}')
            if handler is not None:
                handler()
            handler_prepared = False
            if halt_requested:
                raise Listener.StopException()

        nonlocal handler_prepared
        handler_prepared = True
        PropagatingThread(target=run_handler).start()

    def get_handler_for_key_press(key_mapping):

        def if_key_pressed_in_map(_key_pressed):
            return _key_pressed in key_pressed

        for key, value in key_mapping.items():
            key_list = as_list(key)
            all_pressed = all(if_key_pressed_in_map(k) for k in key_list)
            if all_pressed:
                return value

        return None

    def on_press(key):
        nonlocal handler_prepared

        if halt_requested:
            raise Listener.StopException()

        keyvalue = None
        if hasattr(key, 'vk'):
            keyvalue = key.vk
        else:
            keyvalue = key.name

        if keyvalue in key_pressed:
            return
        key_pressed.add(keyvalue)
        logger.debug(f'press {keyvalue}')

        # handler = keydown_functions.get(keyvalue)
        if handler_prepared:
            return
        else:
            prepare_handler()
        pass

    def on_release(key):
        if halt_requested:
            raise Listener.StopException()

        keyvalue = None
        if hasattr(key, 'vk'):
            keyvalue = key.vk
        else:
            keyvalue = key.name

        logger.debug(f'release {keyvalue}')
        # handler = keyup_functions.get(keyvalue)

        handler = get_handler_for_key_press(keyup_functions)
        if handler is not None:
            handler()
        if keyvalue in key_pressed:
            key_pressed.remove(keyvalue)

        if halt_requested:
            raise Listener.StopException()
        pass

    handler_prepared = False

    if keyup_functions is None:
        keyup_functions = {}

    if keydown_functions is None:
        keydown_functions = {}

    key_pressed = set()

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    pass


def capture_and_convert(end_marker):
    logger.debug('capture running..')
    capture(stop_now=end_marker, begin_callback=beep)
    # logger.debug('convert..')
    # to_mp3()
    logger.debug('to text...')
    as_text = to_text()

    response = agent.run(as_text)
    print(response)

    dispatcher = CommandDispatcher()
    dispatch_response(as_text, dispatcher)


def sample():
    def _start():
        nonlocal recording
        # t = threading.Thread(target=capture_and_convert, args=(_stopped,))
        t = PropagatingThread(target=capture_and_convert, args=(_stopped,))
        recording = True
        t.start()
        pass

    def _stopped():
        return not recording

    def _stop():
        nonlocal recording
        recording = False
        pass


    def parse_keys():
        return {
            "Recording": {
                "Key": "ctrl_r",
                "Action": "to_text"
            }
        }
    
    def make_hashable_keys(key_lookup):
        key_config = parse_keys()
        key_entry = path_get(key_config, key_lookup)
        if isinstance(key_entry, list):
            return tuple(key_entry)
        return key_entry

    recording = False

    raw_watch_config_key_down = {
        make_hashable_keys('Recording.Key'): _start,
    }
    raw_watch_config_key_up = {
        make_hashable_keys('Recording.Key'): _stop,
    }

    sorting_lambda =  lambda item: -len(item) if isinstance(item, tuple) else 0

    watch_config_key_down = {
        k: raw_watch_config_key_down[k] for k in sorted(
            raw_watch_config_key_down.keys(),
            key=sorting_lambda
        )
    }

    watch_config_key_up = {
        k: raw_watch_config_key_up[k] for k in sorted(
            raw_watch_config_key_down.keys(),
            key=sorting_lambda
        )
    }

    del raw_watch_config_key_down
    del raw_watch_config_key_up

    logger.debug(f'watch_config_key_down: {watch_config_key_down}')

    watch_keys(watch_config_key_down, watch_config_key_up)
    pass
