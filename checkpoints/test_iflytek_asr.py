# -*- coding:utf-8 -*-
import base64
import sys
import time
import json
import hashlib
from urllib import request,parse
import aiy.audio

x_appid = "注意！！填入你的应用AppId"
asr_api_key = "注意！！填入你的AIUI平台APIkey"

RECORD_DURATION_SECONDS = 3

 ## 调用科大讯飞提供的Web API
def iflytek_asr(file_path):
    requrl = "https://api.xfyun.cn/v1/aiui/v1/iat"
    cur_time = int(time.time())
    x_param = {"auf":"16k","aue":"raw","scene":"main"}
    x_param = json.dumps(x_param)
    xparam_base64 = base64.b64encode(x_param.encode(encoding="utf-8")).decode().strip('\n')
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

## 使用AIY SDK提供的方法录音，再利用讯飞得到文字识别结果
if __name__ == '__main__':
    with aiy.audio.get_recorder() as recorder:
        while True:
            temp_file, temp_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_file)
            aiy.audio.record_to_wave(temp_path, RECORD_DURATION_SECONDS)
            status_ui.status('stopping')
            result = iflytek_asr(temp_path)
            result_dict = json.loads(result)
            if result_dict['code'] == '00000':
                result_txt = result_dict['data']['result']
                print(result_txt)