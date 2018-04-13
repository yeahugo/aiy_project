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
from pygame import mixer
import aiy.voicehat

x_appid = "5a3e1156"
api_key = "4f8cbbb1c1a64fe1b13198c0d75c3137"

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


RECORD_DURATION_SECONDS = 3


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

def asr(file_path):
    print("python version : .{}".format(sys.version))
    requrl = "https://api.xfyun.cn/v1/aiui/v1/iat"
    print('requrl:{}'.format(requrl))
    #讯飞开放平台注册申请应用的应用ID(APPID)
    #x_appid = "5a60085b";
    print('X-Appid:{}'.format(x_appid))
    #得到当前UTC时间戳
    cur_time = int(time.time())
    print('X-CurTime:{}'.format(cur_time))
    #标准JSON格式参数
    x_param = {"auf":"16k","aue":"raw","scene":"main"}
    x_param = json.dumps(x_param)
    # Base64编码
    xparam_base64 = base64.b64encode(x_param.encode(encoding="utf-8")).decode().strip('\n')
    print('X-Param:{}'.format(xparam_base64))
    #音频文件
    file_data = open(file_path, 'rb')
    file_base64 = base64.b64encode(file_data.read())
    file_data.close()
    body_data = "data="+file_base64.decode("utf-8")
    #ApiKey创建应用时自动生成
    token = api_key + str(cur_time)+ xparam_base64 + body_data
    m = hashlib.md5()
    m.update(token.encode(encoding='utf-8'))
    x_check_sum = m.hexdigest()
    print('X-CheckSum:{}'.format(x_check_sum))
    headers = {"X-Appid": x_appid,"X-CurTime": cur_time,"X-Param":xparam_base64,"X-CheckSum":x_check_sum,"Content-Type":"application/x-www-form-urlencoded"}
    print("headers : {}".format(headers))
    req = request.Request(requrl, data=body_data.encode('utf-8'), headers=headers, method="POST")
    with request.urlopen(req) as f:
        body = f.read().decode('utf-8')
        return body
        print("result body : {}".format(body))

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
            result = asr(temp_path)
            print(result)
         

if __name__ == '__main__':
    try:
        main()
        input('Press Enter to close...')
    except Exception:  # pylint: disable=W0703
        traceback.print_exc()
        input('Press Enter to close...')
