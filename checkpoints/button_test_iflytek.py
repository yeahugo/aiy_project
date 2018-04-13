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
import time
import base64
import hashlib
import threading
import requests
from urllib import request,parse

import aiy.audio  # noqa 
from aiy._drivers._hat import get_aiy_device_name
from pygame import mixer
import aiy.voicehat

x_appid = "5a3e1156"
asr_api_key = "4f8cbbb1c1a64fe1b13198c0d75c3137"
tts_api_key = "8cfb0239801cdb231187c06dc4303ac3"

URL = "http://api.xfyun.cn/v1/service/v1/tts"
AUE = "raw"
APP_ID = '10989863'
API_KEY = 'fRNevkB4V0PjDbCnvjkWM8Pt'
#SECRET_KEY = 'c470690ea39ec1645812db1f3d0d2d02'

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
    configure_driver = os.path.join(AIY_PROJECTS_DIR, 'scripts', 'configure-driver.sh')
    subprocess.check_call(['sudo', configure_driver])

def asr(file_path):
    requrl = "https://api.xfyun.cn/v1/aiui/v1/iat"
    #得到当前UTC时间戳
    cur_time = int(time.time())
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
    token = asr_api_key + str(cur_time)+ xparam_base64 + body_data
    m = hashlib.md5()
    m.update(token.encode(encoding='utf-8'))
    x_check_sum = m.hexdigest()
    headers = {"X-Appid": x_appid,"X-CurTime": cur_time,"X-Param":xparam_base64,"X-CheckSum":x_check_sum,"Content-Type":"application/x-www-form-urlencoded"}
    req = request.Request(requrl, data=body_data.encode('utf-8'), headers=headers, method="POST")
    with request.urlopen(req) as f:
        body = f.read().decode('utf-8')
        return body

def getHeader():
        curTime = str(int(time.time()))
        param = "{\"aue\":\""+AUE+"\",\"auf\":\"audio/L16;rate=16000\",\"voice_name\":\"xiaoyan\",\"engine_type\":\"intp65\"}"
        param_encode = param.encode(encoding="utf-8")
        paramBase64 = base64.b64encode(param_encode).decode().strip('\n')
        m2 = hashlib.md5()
        token = tts_api_key + curTime + paramBase64
        m2.update(token.encode(encoding='utf-8'))
        checkSum = m2.hexdigest()
        header ={
                'X-CurTime':curTime,
                'X-Param':paramBase64,
                'X-Appid':x_appid,
                'X-CheckSum':checkSum,
                'X-Real-Ip':'127.0.0.1',
                'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
        }
        return header

def getBody(text):
        data = {'text':text}
        return data

def writeFile(file, content):
    with open(file, 'wb') as f:
        f.write(content)
    f.close()


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
            result_dict = json.loads(result)
            if result_dict['code'] == '00000':
                result_txt = result_dict['data']['result']
                print(result_txt)
                r = requests.post(URL,headers=getHeader(),data=getBody(result_txt))
                contentType = r.headers['Content-Type']
                if contentType == "audio/mpeg":
                    sid = r.headers['sid']
                    audio_filepath = "audio/"
                    if AUE == "raw":
                        audio_filepath += sid + ".wav"
                        
                    else :
                        audio_filepath += sid + ".mp3"
                        writeFile("audio/"+sid+".mp3", r.content)
                    print("success, sid = " + sid)
                    writeFile(audio_filepath, r.content)
                    mixer.init()
                    mixer.music.load(audio_filepath)
                    mixer.music.play()
                else :
                    print(r.text) 
         

if __name__ == '__main__':
    try:
        main()
        input('Press Enter to close...')
    except Exception:  # pylint: disable=W0703
        traceback.print_exc()
        input('Press Enter to close...')
