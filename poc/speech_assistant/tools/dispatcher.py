
import re
import pyperclip
from tools.sound_tools import beep, ok_beep, bad_beep
from api.lib.logger import Logger
from pynput.keyboard import Listener

logger = Logger('dispatcher', file_handler=False).getLogger()

halt_requested = False

def normalized(text):
    if text is None:
        return ''

    if len(text) == 0:
        return ''

    last_char = text[-1]
    if last_char in '.!,;':
        text = text[:-1]
    return text.lower()


history = []
things_to_remember = []


class CommandDispatcher:
    def dispatch(self, command):
        command_line = command.split()
        # intro = command_line[0]
        command = normalized(command_line[1])
        history.append({'command': command_line, 'error': None})

        handler = None
        if hasattr(self, command):
            handler = getattr(self, command)
        elif len(command_line) >= 3:
            second_word = normalized(command_line[2])
            second_try = f'{command}_{second_word}'
            if hasattr(self, second_try):
                handler = getattr(self, second_try)

        if handler is not None:
            handler(command_line)
            ok_beep()
        else:
            self._invalid_command(command_line, f'no such command "{command}"')
            bad_beep()

    def __call__(self, *args, **kwargs):
        self.dispatch(args[0])

    def _invalid_command(self, command_line, comment=None):
        global history
        history[-1]['error'] = comment
        logger.error(
            f'Error processing command: {"" if comment is None else comment}:')
        logger.debug(str(command_line))

    def exit(self, args):
        global halt_requested
        halt_requested = True

    def language(self, args):
        languages = {
            'english': 'en',
            'englisch': 'en',
            'german': 'de',
            'deutsch': 'de'
        }
        wanted = normalized(args[2])
        language_code = languages.get(wanted, 'en')
        global current_language
        current_language = language_code
        logger.info(f'language set to {current_language}')

    def to_do(self, args):
        if len(args) > 3:
            things_to_remember.append(' '.join(args[3:]))

    def memory(self, args):
        logger.debug(str(things_to_remember))
        pyperclip.copy(str(things_to_remember))

    def history(self, args):
        h = str(history)
        logger.debug(h)
        pyperclip.copy(h)


# command_pattern = re.compile(r'^[Cc]ommand ')
command_pattern = re.compile(r'^[Aa]ction[.!]? ')


def dispatch_response(transcript, command_dispatcher):
    text = transcript.get('text', '???')
    if command_pattern.match(text):
        command_dispatcher(text)
        if halt_requested:
            raise Listener.StopException()
    else:
        pyperclip.copy(transcript.get('args', 'No args detected').get(
            'output', 'No output detected'))
        beep()
