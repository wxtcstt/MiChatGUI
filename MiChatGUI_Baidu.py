import sys
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,QRadioButton,QDesktopWidget,QTextEdit,QFrame,QMessageBox,QButtonGroup
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
from pathlib import Path
import os
import json
from miaccount   import   MiAccount
from minaservice import   MiNAService
from miioservice import   MiIOService
from miiocommand import  miio_command
from aiohttp     import   ClientSession
from pathlib     import   Path
import os
import json
import asyncio
import time
from http.cookies import SimpleCookie
from requests.utils import cookiejar_from_dict
from threading import Thread
from queue import Queue
import requests
from threading import Event
gptmsg_queue=Queue()
audio_threadevent = Event()

class LoginWindow(QWidget):
    alert = pyqtSignal(str) 
    logevent=pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle('小米音箱服务 github库名字MiChatGUI')
        
        connectmode_select_box = QHBoxLayout()
        connectmode_selectbg = QButtonGroup()
        self.connectrb1 = QRadioButton('接入方式1')
        self.connectrb1.setChecked(True)
        connectmode_select_box.addWidget(self.connectrb1)
        self.connectrb2 = QRadioButton('接入方式2')
        connectmode_select_box.addWidget(self.connectrb2)
        connectmode_select_box.addStretch()
        self.connectrb1.clicked.connect(self.connect_mode_select)
        self.connectrb2.clicked.connect(self.connect_mode_select)
        connectmode_selectbg.addButton(self.connectrb1)
        connectmode_selectbg.addButton(self.connectrb2)
        # 创建用于输入用户名、密码和设备型号的文本输入框
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.device_input = QLineEdit()
        self.did_input = QLineEdit()
        self.tts_input=QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        username_label = QLabel('你的ID:')
        password_label = QLabel('你的密码:')
        device_label = QLabel('你的设备型号:')
        self.did_label = QLabel('DID(设备ID):')
        self.tts_input_label = QLabel('语音命令:')
        self.login_button = QPushButton('开始')
        self.login_button.clicked.connect(self.on_login_button_clicked)
        speaker_label = QLabel('小爱音箱名字:')
        self.speaker_input = QLineEdit()
        # 创建用于排列以上控件的垂直布局器
        input_layout = QHBoxLayout()
        input_layout.addWidget(username_label)
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(password_label)
        input_layout.addWidget(self.password_input)
        input_layout.addWidget(device_label)
        input_layout.addWidget(self.device_input)
        input_layout.addWidget(speaker_label)
        input_layout.addWidget(self.speaker_input )
        input_layout.addWidget( self.did_label)
        input_layout.addWidget(self.did_input)
        input_layout.addWidget( self.tts_input_label)
        input_layout.addWidget(self.tts_input)
        self.did_label.hide()
        self.did_input.hide()
        self.tts_input_label.hide()
        self.tts_input.hide()
        input_layout.addWidget(self.login_button)
        #百度配置部分
        baidu_layout = QHBoxLayout()
        baiduapikey_label = QLabel('百度ApiKey:')
        self.baiduapikey_input = QLineEdit()
        baidusecretkey_label = QLabel('百度SecretKey:')
        self.baidusecretkey_input = QLineEdit()
        baidu_layout.addWidget(baiduapikey_label)
        baidu_layout.addWidget(self.baiduapikey_input)
        baidu_layout.addWidget(baidusecretkey_label)
        baidu_layout.addWidget(self.baidusecretkey_input)
        
        # 创建用于显示图片的标签
        imagesize=200
        img_label = QLabel(self)
        pixmap = QPixmap('fox.png')
        pixmap = pixmap.scaledToHeight(imagesize)
        img_label.setPixmap(pixmap)
        self.logtext= QTextEdit()
        image_layout = QHBoxLayout()
        image_layout.addWidget(img_label)
        image_layout.addWidget(self.logtext)
        #测试你的服务器
        hint_label = QLabel('设置你的GPT消息前缀')
        gpthint_labelLayout=QHBoxLayout()
        self.gptprefix=QLineEdit()
        self.gptprefix.setText("正在问大哥GPT")
        gpthint_labelLayout.addWidget(hint_label)
        gpthint_labelLayout.addWidget(self.gptprefix)
        test_label = QLabel('测试一下你的服务器')
        testServiceLayout=QVBoxLayout()
    
        self.testAsk=QLineEdit()
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        testServiceLayout.addWidget(line)
        testServiceLayout.addWidget(test_label)
       
       
       
        askLayout=QHBoxLayout()
        askLayout.addWidget( self.testAsk)
        self.testAskSend=QPushButton("发送")
        askLayout.addWidget( self.testAskSend)
        self.testAskSend.clicked.connect(self.on_testAskSend_clicked)
        testServiceLayout.addLayout(askLayout)
        
        layout = QVBoxLayout()
        layout.addLayout(connectmode_select_box)
        layout.addLayout(input_layout)
        layout.addLayout(baidu_layout)
        layout.addLayout(image_layout)
        layout.addLayout(gpthint_labelLayout)
        
        layout.addLayout(testServiceLayout)
        layout.addStretch()
        self.setLayout(layout)
        self.loopflag=True
        self.started=False
       
        self.alert.connect(self.deviceInvalid) 
        self.logevent.connect(self.logPrint) 
        self.testaskthread=None
        self.center_window()
        #开启百度llm线程
        self.ask_Thread=Thread(target=self.gptaskthread)
        self.ask_Thread.start()
        
        self.askQueue=Queue(maxsize=1)
        self.baidullm=BaiduLLM("","")
        self.Iservice=None
        self.IOservice=None
        self.Ideviceid=""
        self.is_gptmode=False
        self.ConnectMode=1
        self.MI_DID=""
        self.baiduappkey=""
        self.baidusecretkey=""
        self.readUserInfo()
        self.baidullm=BaiduLLM(self.baiduappkey,self.baidusecretkey)
        
        
    def logPrint(self,msg):
        result=self.logtext.toPlainText()+msg+"\n"
        linarray=result.split("\n")
        if len(linarray)>20:
            linarray=linarray[-20:]
        result="\n".join([item  for item in linarray if item])
        # # if result[-1]!="\n":
        result+="\n"
        self.logtext.setText(result)
    
    def run_thread(self,task, args):
        thread = Thread(target=task, args=args)
        thread.start()
        return thread
    
    def test_asl_threadfunc(self,query):
        try:
            if not self.baidullm.API_KEY and self.baiduappkey:
                self.baidullm.API_KEY=self.baiduappkey
                self.baidullm.SECRET_KEY=self.baidusecretkey
                
            result=self.baidullm.llm(query)
            #result=self.ask(query)
            # self.logPrint(result)
            if result=="-1":
                self.logevent.emit("无法连接ChatGPT服务器这可能是你的网络代理的问题")
            else:
                self.logevent.emit(result)
            self.testAsk.setText("")
        except Exception as e:
            print(e)
        
        
    def on_testAskSend_clicked(self):
        if(self.testAsk.text()!=""):
            print(self.testAsk.text())
            # 使用Lambda函数创建线程
            print(self.testaskthread.isAlive() if self.testaskthread else "")
            if  self.testaskthread==None or not self.testaskthread.isAlive():
                self.testaskthread = Thread(target=self.test_asl_threadfunc, args=(self.testAsk.text(),))
                self.testaskthread.start()           
 
    def center_window(self):
        desktop = QDesktopWidget()
        # 获取桌面大小
        screen_size = desktop.screenGeometry()
        # 获取窗口大小
        window_size = self.geometry()
        # 计算窗口在桌面中间应该显示的位置
        x = (screen_size.width() - window_size.width()) // 2
        y = (screen_size.height() - window_size.height()) // 2
        # 设置窗口的位置
        self.setGeometry(x, y, 1000, 400)
        self.move(x, y)
        
    def connect_mode_select(self):
        '''接入方式1'''
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.text()=="接入方式1":
                self.ConnectMode=1
                self.did_label.hide()
                self.did_input.hide()
                self.tts_input_label.hide()
                self.tts_input.hide()
            elif radioButton.text()=="接入方式2":
                self.ConnectMode=2
                self.did_label.show()
                self.did_input.show()
                self.tts_input_label.show()
                self.tts_input.show()
                
    def radioClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.text()=="OpenAI":
                print("你将直接调用openai服务")
                self.openai_config.show()
                self.usercustom_config.hide()
                self.auther_config.hide()
                self.ApiMode=1
                
                self.setFixedSize(1000, 400)
            elif radioButton.text()=="你的自定义服务":
                print("你将使用你的自定义服务")
                self.openai_config.hide()
                self.usercustom_config.show()
                self.auther_config.hide()
                self.ApiMode=2
                self.setFixedSize(1000, 700)
                
            elif "作者的免费测试" in radioButton.text():
                print("你将作者的免费测试(仅限最多50个问题)")
                self.openai_config.hide()
                self.usercustom_config.hide()
                self.auther_config.show()
                self.ApiMode=3
                self.resize(1000, 700)
                
            print("选中了：" + radioButton.text())
            
    def readUserInfo(self):
        if os.path.exists(os.path.join(str(Path.home()), ".michatgpt.token")):
            with open(os.path.join(str(Path.home()), ".michatgpt.token")) as f:
                s= f.read()
                try:
                    user_data=json.loads(s)
                    self.username_input.setText(user_data["userid"])
                    self.password_input.setText(user_data["password"])
                    self.device_input.setText(user_data["model"])
                    self.speaker_input.setText(user_data["speakername"])
                    if "baiduappkey" in user_data:
                        self.baiduapikey_input.setText(user_data["baiduappkey"])
                        self.baidusecretkey_input.setText(user_data["baidusecretkey"])
                        self.baiduappkey=user_data["baiduappkey"]
                        self.baidusecretkey=user_data["baidusecretkey"]
        
                    if "did" in user_data:
                        self.did_input.setText(user_data["did"])
                    if "tts" in user_data:
                        self.tts_input.setText(user_data["tts"])
                    if "connectmode" in user_data and user_data["connectmode"]!="":
                        self.ConnectMode=user_data["connectmode"]
                        if  self.ConnectMode==2:
                            self.connectrb2.setChecked(True)
                            self.did_label.show()
                            self.did_input.show()
                            self.tts_input_label.show()
                            self.tts_input.show()
                            
                except Exception as e:
                    print(e)
    
    def saveconfig(self):
        ''''''
        try:
            username = self.username_input.text()
            password = self.password_input.text()
            device = self.device_input.text()
            speakername=self.speaker_input.text()
            gptmode="1"
            baiduappkey=self.baiduapikey_input.text() 
            baidusecretkey=self.baidusecretkey_input.text()
        
            with open(os.path.join(str(Path.home()), ".michatgpt.token"),'w') as f:
                info={"userid":username,"password":password,"model":device,"speakername":speakername,"chatgptkey":"","usercode":"","did":self.did_input.text(),
                      "tts":self.tts_input.text(),"connectmode":self.ConnectMode,"gptmode":gptmode,"baiduappkey":baiduappkey,"baidusecretkey":baidusecretkey}
                f.write(json.dumps(info))
        except Exception as e:
            print(e)
    def on_login_button_clicked(self):
        ''' 在点击登录按钮时触发这个事件处理函数
            获取文本输入框中用户输入的内容
        '''
        self.saveconfig()
        if self.started==True:
            self.loopflag=False
            time.sleep(0.5)
            self.login_button.setText("开始")
        else:
            self.loopflag=True
            thread=Thread(target=self.xiaomi_thread_func)
            thread.start()
            self.started=True
            self.login_button.setText("停止")
    async def appmain(self):

        task1 = asyncio.create_task(self.xiaomimain())
        task2 = asyncio.create_task(self.loop_say_something())
        await task1
        await task2
        print(f"Finished Tasks: {time.strftime('%X')}")
    
    def xiaomi_thread_func(self):
        ''''''
        if not self.baidullm.API_KEY and self.baiduappkey:
                self.baidullm.API_KEY=self.baiduappkey
                self.baidullm.SECRET_KEY=self.baidusecretkey
                self.baidullm.create_token()
        asyncio.run(self.appmain())
        
    def get_last_timestamp_and_record(self,data):
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
    def parse_cookie_string(self,cookie_string):
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        cookies_dict = {}
        cookiejar = None
        for k, m in cookie.items():
            cookies_dict[k] = m.value
            cookiejar = cookiejar_from_dict(cookies_dict, cookiejar=None, overwrite=True)
        return cookiejar
    def  deviceInvalid(self):
        self.started=False
        self.login_button.setText("开始")
        QMessageBox.warning(self,"警告","没有找到你的音箱")
    def findttsCommand(self,s):
        ttscommand=""
        try:
            index=s.index("Device_Information")
            if index<0:
                index=0
            if index>=0:
                s=s[index:]
                d = {}
                
                for line in s.strip().split('\n'):
                    if "Intelligent_Speaker" in line or "_Play_Text" in line:
                        if '=' in line and 'Intelligent_Speaker' in line:
                            key, value = line.split('=')
                            d[key.strip()] = value.strip()
                        if  '=' in line and "_Play_Text" in line:
                            index=line.index('#')
                            if index>=0:
                                line=line[0:index]
                            key, value = line.split('=')
                            d[key.strip()] = value.strip()
                            
                intelligent_speaker_value = d['Intelligent_Speaker']
                play_text_value = d['_Play_Text'] 
                ttscommand=intelligent_speaker_value+"-"+play_text_value
        except Exception as e:  
            print(e)
        return ttscommand
   
   
    #小米音箱部分--------------------------------------
    def gptaskthread(self):
        while True:
            try:
                query=self.askQueue.get()
                if  self.is_gptmode:
                    self.baidullm.llm_stream(query)
            except Exception as e:
                pass
            time.sleep(0.1)
        
    def  _getMsgFromQueue(self):
        try:
            msg=gptmsg_queue.get_nowait()
            return msg
        except Exception as e:
            return ""

    async def loop_say_something(self):
        concatmsg=""
        while True:  
            _gptmsg=self._getMsgFromQueue()
            if audio_threadevent.isSet(): #本次请求取消
                concatmsg,_gptmsg="",""
            if _gptmsg and _gptmsg!="EOF":
                if concatmsg:
                   _gptmsg=concatmsg+_gptmsg
                if _gptmsg and len(_gptmsg)<12:
                    concatmsg=_gptmsg
                    continue
            else:
                if concatmsg!="":
                    _gptmsg=concatmsg
                else:
                    _gptmsg=""

            if _gptmsg: 
                concatmsg=""
                try:
                    self.logevent.emit(_gptmsg)  
                    if self.ConnectMode==1:
                            await self.Iservice.text_to_speech(self.Ideviceid, _gptmsg)
                    else:
                            await miio_command(self.IOservice, self.MI_DID, _gptmsg)
                                        
                    #await self.Iservice.text_to_speech(self.Ideviceid, _gptmsg)
                    
                    while True:
                        playing_info = await self.Iservice.player_get_status(self.Ideviceid)
                        is_playing = (json.loads(playing_info.get("data", {}).get("info", "{}")).get("status", -1) == 1)
                        if not is_playing:
                            break
                        await asyncio.sleep(0.2) 
                except Exception as e:
                    pass 
            await asyncio.sleep(0.1) 


   
    async def xiaomimain(self):
        global audio_threadevent
        lastmsg=""
        try:
            hardware,user_id,password=self.device_input.text(), self.username_input.text(),self.password_input.text()
            wifispeaker_name=self.speaker_input.text()
            MI_DID=""
            #---------------------------
            LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"
            COOKIE_TEMPLATE = "deviceId={device_id}; serviceToken={service_token}; userId={user_id}"
            lastTimeStamp=int(time.time()* 1000)
            async with ClientSession() as session:
                account = MiAccount(session,user_id,password,"./.mi.token")
                if self.ConnectMode==2:
                    ioservice = MiIOService(account)
                    self.IOservice=ioservice
                    deviceresult = await miio_command(ioservice, MI_DID, "list", '')
                    print(deviceresult)
                    for item in deviceresult:
                        if item["name"]==wifispeaker_name:
                            MI_DID=item["did"]
                            self.MI_DID=MI_DID
                            if  self.did_input.text()=="":
                                self.did_input.setText(MI_DID)
                            MODEl=item["model"]
                            if MODEl and self.tts_input.text()=="":
                                    modelresult = await miio_command(ioservice, MI_DID, f"spec {MODEl}", '')
                                    ttscommand=self.findttsCommand(modelresult)
                                    self.tts_input.setText(ttscommand)
                            break
                    self.saveconfig()
                           
                await account.login("micoapi")
                service = MiNAService(account)#通过这个发送消息
                self.Iservice=service
                deviceresult = await service.device_list()
                if not isinstance(deviceresult, str):
                    deviceid=None
                    for h in deviceresult:
                        if h.get("name", "") == wifispeaker_name:
                            deviceid = h.get("deviceID")
            
                    if not deviceid:
                        print("无法找到设备....")
                    print("deviceid:",deviceid)
                    self.Ideviceid=deviceid
                    with open("./.mi.token") as f:
                        user_data=json.loads(f.read())
                    service_token=user_data.get("micoapi")[1]
                    cookiestr=COOKIE_TEMPLATE.format(
                    device_id=deviceid,
                    service_token=service_token,
                    user_id=user_id,
                    )
                    cookie = self.parse_cookie_string(cookiestr)
                if not deviceid:
                    self.alert.emit("没有找到你的音箱")
                    return 0
                self.logevent.emit("找到了你的音箱:"+deviceid)
                async def get_if_xiaoai_is_playing(): #测试音乐播放
                            playing_info = await service.player_get_status(deviceid)
                            is_playing = (
                                json.loads(playing_info.get("data", {}).get("info", "{}")).get("status", -1) == 1
                            )
                            return is_playing
                while self.loopflag:
                    r = await session.get(
                        LATEST_ASK_API.format(
                            hardware=hardware, timestamp=str(int(time.time()* 1000))
                        ),
                        cookies=self.parse_cookie_string(cookie))
                    chatmsg=await r.json()
                    new_timestamp, last_record = self.get_last_timestamp_and_record(chatmsg)
                    if last_record!=lastmsg:
                        lastmsg=last_record
                        print("最后的问答：",last_record)
                        self.logevent.emit(last_record)
                    if last_record and new_timestamp>lastTimeStamp:
                        lastTimeStamp=int(time.time()*1000)
                      
                        if last_record in ["大头模式" ,"进入大头模式","文心一言模式","进入文心一言模式"]:
                            self.is_gptmode=True
                            await service.text_to_speech(deviceid, "进入大头模式")
                            continue
                        elif last_record in ["退出大头模式","退出文心一言模式","退出文心一言"] :
                            await service.text_to_speech(deviceid, "好的")
                            self.is_gptmode=False
                            continue
                       
                        if   "停止" in last_record or "休息"==last_record or  "休息一下"==last_record or  "声音调到" in last_record and\
                                "关闭"== last_record or "停止回答" in last_record or "停止播放" in last_record or "请播放" in last_record or "播放音乐" in last_record:
                                    continue      
                                       
                        if self.is_gptmode==True:
                            self.logevent.emit("发现新消息，送往GPT请求问答")   
                            audio_threadevent.set()
                            while True:
                                try:
                                    gptmsg_queue.get(timeout=0.01)
                                except Exception as e:
                                    print("消息队列中的缓存清空完毕...")
                                    break
                            if self.askQueue.qsize()==0:
                                audio_threadevent.clear()
                                message="正在问GPT请等待"
                                try:
                                    if self.ConnectMode==1:
                                        await service.text_to_speech(deviceid, message)
                                    else:
                                        await miio_command(ioservice, MI_DID, message)
                                except Exception as e:
                                    print(e)
                                self.askQueue.put(last_record)               
                    await asyncio.sleep(0.3)                 
        except Exception as e:
            self.logevent.emit(str(e))
            print(e)

        self.started=False
        print("结束小米线程")
        self.login_button.setText("开始")


class  BaiduLLM():
    def __init__(self,_API_KEY="",_SECRET_KEY="") -> None:
        self.API_KEY=_API_KEY
        self.SECRET_KEY=_SECRET_KEY
        self.CHINESE_END_SIGN=["。","？","！","，","；"]
        self.token=""
        if self.API_KEY:
            self.create_token()
    
    def create_token(self):
        params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
        try:
            newtoken=str(requests.post("https://aip.baidubce.com/oauth/2.0/token", params=params).json().get("access_token"))
            with open(os.path.join(str(Path.home()), ".baidullm.token"),'w') as f:
                info={"token":newtoken,"timestamp":int(time.time())}
                f.write(json.dumps(info))
            self.token=newtoken
        except Exception as e:
            print(e)

    def  llm(self,content):
        leftmsg=""
        if not   self.token:
            self.create_token()
        if   self.token:
            try:
                url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + self.token
                payload = json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": content
                        },   
                    ]
                    ,
                    "stream":True
                })
                headers = {
                    'Content-Type': 'application/json'
                }
               
                response = requests.request("POST", url, headers=headers, data=payload,stream=True)   
                for item in response.iter_lines():
                    itemstr=item.decode(encoding='utf8')
                    if "data:" in itemstr:
                        itemstr=itemstr[6:]
                        jsondic=json.loads(itemstr)
                        for chr in jsondic["result"]:
                            leftmsg+=chr        
            except Exception as e:
                print("Error:",e)
            return leftmsg       
        else:
            print("token invalid.............")
            return "token invalid............."
    
    def  llm_stream(self,content):
            global gptmsg_queue
            if   self.token:
                try:
                    
                    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + self.token
                    payload = json.dumps({
                        "messages": [
                            {
                                "role": "user",
                                "content": content
                            },   
                        ]
                        ,
                        "stream":True
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    leftmsg=""
                    response = requests.request("POST", url, headers=headers, data=payload,stream=True)   
                    for item in response.iter_lines():
                        itemstr=item.decode(encoding='utf8')
                        if "data:" in itemstr:
                            itemstr=itemstr[6:]
                            jsondic=json.loads(itemstr)
                            for chr in jsondic["result"]:
                                leftmsg+=chr
                                if leftmsg[-1] in self.CHINESE_END_SIGN:
                                    gptmsg_queue.put(leftmsg.replace("*",""))
                                    print(leftmsg)
                                    leftmsg=""        
                except Exception as e:
                    print("Error:",e)
                finally:
                    print("获取全部的回答........")
                    gptmsg_queue.put("EOF")
                   
            else:
                print("token invalid.............")
                return ""
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    icon = QIcon('icon.png')
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())