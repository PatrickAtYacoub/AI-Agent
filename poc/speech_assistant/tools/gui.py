
import os
if os.name == 'nt':
    import ctypes

if os.name == 'nt':
    def show_message_box(message):
        ctypes.windll.user32.MessageBoxW(
            0, message, "LLM Response", 0x40 | 0x1000)
elif os.name == 'posix':
    def show_message_box(message):
        try:
            # Try to use zenity first
            subprocess.run(['zenity', '--info', '--text', message])
        except FileNotFoundError:
            # Fallback to notify-send if zenity is not installed
            subprocess.run(['notify-send', message])
else:
    def show_message_box(message):
        logger.debug(message)