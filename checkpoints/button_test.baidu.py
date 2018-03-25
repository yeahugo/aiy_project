#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Check that the voiceHAT audio input and output are both working."""


import fileinput
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import traceback
import json
import threading

import aiy.audio  # noqa
from aiy._drivers._hat import get_aiy_device_name
from aip import AipSpeech
from pygame import mixer
import aiy.voicehat

APP_ID = '10989863'
API_KEY = 'fRNevkB4V0PjDbCnvjkWM8Pt'
SECRET_KEY = 'c470690ea39ec1645812db1f3d0d2d02'
baidu_client = AipSpeech(APP_ID,API_KEY,SECRET_KEY)

AIY_PROJECTS_DIR = os.path.dirname(os.path.dirname(__file__))

CARDS_PATH = '/proc/asound/cards'
CARDS_ID = {
        "Voice Hat": "googlevoicehat",
        "Voice Bonnet": "aiy-voicebonnet",
        }

STOP_DELAY = 1.0

TEST_SOUND_PATH = '/usr/share/sounds/alsa/Front_Center.wav'

RECORD_DURATION_SECONDS = 3


def ask(prompt):
    """Get a yes or no answer from the user."""
    ans = input(prompt + ' (y/n) ')

    while not ans or ans[0].lower() not in 'yn':
        ans = input('Please enter y or n: ')

    return ans[0].lower() == 'y'


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


##"""Check the microphone records correctly."""
    #aiy.voicehat.get_button().on_press(on_button_pressed)
    #return ask('Did you hear your own voice?')


def enable_audio_driver():
    print("Enabling audio driver for VoiceKit.")
    configure_driver = os.path.join(AIY_PROJECTS_DIR, 'scripts', 'configure-driver.sh')
    subprocess.check_call(['sudo', configure_driver])


def main():
    with aiy.audio.get_recorder() as recorder:
        while True:
            status_ui = aiy.voicehat.get_status_ui()
            status_ui.status('ready')
            button = aiy.voicehat.get_button()
            button.wait_for_press()
            status_ui.status('listening')

            temp_file, temp_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_file)
            print('Recording...')
            aiy.audio.record_to_wave(temp_path, RECORD_DURATION_SECONDS)
            print('Playing back recorded audio...')
            status_ui.status('stopping')
            result = baidu_client.asr(get_file_content(temp_path),'wav',16000,{'lan':'zh',})
            try:
                if result['err_no'] == 0:
                    result_txt = result['result'][0]
                    result = baidu_client.synthesis(result_txt,'zh',1,{'vol':1})
                    if not isinstance(result,dict):
                        with open('audio.mp3','wb') as f:
                            f.write(result)
                    mixer.init()
                    mixer.music.load('audio.mp3')
                    mixer.music.play()
            finally:
                try:
                    os.unlink(temp_path)
                except FileNotFoundError:
                    pass
         

if __name__ == '__main__':
    try:
        main()
        input('Press Enter to close...')
    except Exception:  # pylint: disable=W0703
        traceback.print_exc()
        input('Press Enter to close...')
