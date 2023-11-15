from miservice import MiAccount
from miservice import MiNAService
from aiohttp import ClientSession
from http.cookies import SimpleCookie
from requests.utils import cookiejar_from_dict
from pathlib import Path
import os,json,time,asyncio
def get_last_timestamp_and_record(data):
        if "data" in data:
            d= data.get("data")
            records = json.loads(d).get("records")
            if not records:
                return 0, None
            last_record = records[0]
            timestamp = last_record.get("time")
            return timestamp, last_record["query"]
        else:
             return 0, None
def parse_cookie_string(cookie_string):
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies_dict = {}
    cookiejar = None
    for k, m in cookie.items():
        cookies_dict[k] = m.value
        cookiejar = cookiejar_from_dict(cookies_dict, cookiejar=None, overwrite=True)
    return cookiejar

music_collection={"如愿":"http://192.168.0.105:15005/ruyuan.wav","像我这样的人":"http://192.168.0.105:15005/xiangwozheyangderen.flac"}
async def main():
    is_musicmode=False
    try:
        #-------------------------用户配置输入你的小音箱的型号
        hardware,user_id,password="L15A","179404957","12345678"
        wifispeaker_name="客厅小米音箱"
        LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"
        COOKIE_TEMPLATE = "deviceId={device_id}; serviceToken={service_token}; userId={user_id}"
        lastTimeStamp=int(time.time()* 1000)
        
        async with ClientSession() as session:
            account = MiAccount(session,user_id,password,os.path.join(str(Path.home()),".mi.token"),)
            await account.login("micoapi")
            service = MiNAService(account)
            deviceresult = await service.device_list()
            if not isinstance(deviceresult, str):
                deviceid=None
                for h in deviceresult:
                  if h.get("name", "") == wifispeaker_name:
                    deviceid = h.get("deviceID")
                if not deviceid:
                    print("无法找到设备，已退出")
                    return
                print("deviceid:",deviceid)
                with open(os.path.join(str(Path.home()), ".mi.token")) as f:
                    user_data=json.loads(f.read())
                service_token=user_data.get("micoapi")[1]
                cookiestr=COOKIE_TEMPLATE.format(
                device_id=deviceid,
                service_token=service_token,
                user_id=user_id,
                )
                cookie = parse_cookie_string(cookiestr)
            while True:
                r = await session.get(
                    LATEST_ASK_API.format(
                        hardware=hardware, timestamp=str(int(time.time()* 1000))
                    ),
                    cookies=parse_cookie_string(cookie))
                chatmsg=await r.json()
                new_timestamp, last_record = get_last_timestamp_and_record(chatmsg)
                if last_record and new_timestamp>lastTimeStamp:
                    lastTimeStamp=new_timestamp
                    print("有新的提问出现,",last_record)
                    if last_record=="大头模式" or last_record=="进入大头模式" :
                        is_musicmode=True
                        await service.text_to_speech(deviceid, "我爱大头")
                        await asyncio.sleep(0.5)
                        continue
                    elif last_record=="退出大头模式" or last_record=="退出大头" :
                        await service.text_to_speech(deviceid, "好的")
                        await asyncio.sleep(0.5)
                        is_musicmode=False
                        continue
                    if is_musicmode==True and   "播放" in  last_record:
                            prefixindex=last_record.find("播放")
                            songname=last_record[prefixindex+2:]
                            if songname:
                                if songname in music_collection:
                                    await asyncio.sleep(1) 
                                    await service.text_to_speech(deviceid, "好的")
                                    await asyncio.sleep(0.5) 
                                    print("@@@@@@@@@@@@@播放音乐:",songname)
                                    songurl=music_collection[songname]
                                    await service.play_by_url(deviceid,songurl)
                await asyncio.sleep(0.3)                 
    except Exception as e:
        print(e)
         
async def appmain():
    task1 = asyncio.create_task(main())
    await task1
def  appthread():
    asyncio.run(appmain())

#----------------------定义一个flask服务器
from flask import  Flask
from flask_cors import CORS
from threading import Thread
app =  Flask(__name__,static_url_path='')
cors = CORS(app,resources = {r"/api/*":{"origins":"*"}})
cors = CORS(app,supports_credentials= True)  
if __name__ =='__main__':
    try:
        xiaoaithread=Thread(target=appthread)
        xiaoaithread.start()
        print("web server started......")
        app.run(host='0.0.0.0',port=15005) 
    except Exception as e:
        print(e)
    except KeyboardInterrupt as e:
        print(e)
   