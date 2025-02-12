# import os
# import sys

# current_dir = os.path.dirname(os.path.realpath(__file__))

# parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
# lib_dir = os.path.join(parent_dir, 'lib')
# sys.path.append(lib_dir)

# from apicall import api

# print(api.send_request('whisper', 'speech.mp3'))


from whisper import sample

sample()