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
import requests
from threading import Thread
import uuid
from chatgptbot import ChatGPTBot
mac_addr = uuid.getnode()
mac_address = ':'.join(("%012X" % mac_addr)[i:i+2] for i in range(0, 12, 2))
print("MAC 地址：", mac_address)
from usercustombot  import UserCustomBot

        
class LoginWindow(QWidget):
    alert = pyqtSignal(str) 
    logevent=pyqtSignal(str)
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
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
        # 将密码输入框设置为密码模式
        self.password_input.setEchoMode(QLineEdit.Password)

        # 创建用于显示标签的标签
        username_label = QLabel('你的ID:')
        password_label = QLabel('你的密码:')
        device_label = QLabel('你的设备型号:')
        self.did_label = QLabel('DID(设备ID):')
        self.tts_input_label = QLabel('语音命令:')
        # 创建登录按钮
        self.login_button = QPushButton('开始')

        # 绑定登录事件
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
        
        # 创建用于显示图片的标签
        imagesize=200
        img_label = QLabel(self)
        pixmap = QPixmap('fox.png')
        pixmap = pixmap.scaledToHeight(imagesize)
        img_label.setPixmap(pixmap)
        self.logtext= QTextEdit()
    
        
        
        service_select_box = QHBoxLayout()
        rb1 = QRadioButton('OpenAI')
        rb1.setChecked(True)
        service_select_box.addWidget(rb1)
        rb2 = QRadioButton('你的自定义服务')
        service_select_box.addWidget(rb2)
        #rb3 = QRadioButton('作者的免费测试(仅限最多50个问题)', self)
        #service_select_box.addWidget(rb3)
        service_select_box.addStretch()
        rb1.clicked.connect(self.radioClicked)
        rb2.clicked.connect(self.radioClicked)
        self.service_selectbg = QButtonGroup()
        self.service_selectbg.addButton(rb1)
        self.service_selectbg.addButton(rb2)
        #服务的设置
        service_config_box = QHBoxLayout()
        self.openai_config=self.createOpenAIConfigPanel()
        self.usercustom_config=self.createUserCustomonfigPanel()
        self.auther_config=QLabel("使用作者的服务器做个测试")
        service_config_box.addWidget(self.openai_config)
        service_config_box.addWidget(self.usercustom_config)
        service_config_box.addWidget(self.auther_config)
        self.openai_config.show()
        self.usercustom_config.hide()
        self.auther_config.hide()
        #图片水平排列
        image_layout = QHBoxLayout()
        image_layout.addWidget(img_label)
        image_layout.addWidget(self.logtext)
        # image_layout.addWidget(zhifubao_label)
        #测试你的服务器
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
        layout.addLayout(service_select_box)
        layout.addLayout(service_config_box)
        layout.addLayout(image_layout)
        layout.addLayout(testServiceLayout)
        layout.addStretch()
        
        # 设置该窗口的布局器为垂直布局器
        self.setLayout(layout)
        self.ApiMode=1 #1 openapi 2 自定义服务 3 作者的测试服务器
        
        self.loopflag=True
        self.started=False
        self.center_window()
        
        self.ConnectMode=1 #1 连接方式 2 连接方式2 
        self.readUserInfo()
        self.chatgpt_bot=ChatGPTBot(self.openaikey_input.text())
        self.alert.connect(self.deviceInvalid) #
        self.logevent.connect(self.logPrint) #
        self.testaskthread=None
      
        
    
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
            result=self.ask(query)
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
        
    def createOpenAIConfigPanel(self):
        panel=QWidget()
        panel_layout = QHBoxLayout()
        panel_label = QLabel('请输入你的OpenAI Key:')
        self.openaikey_input = QLineEdit()
        self.openaikey_button = QPushButton('确定')
        self.openaikey_button.clicked.connect(self.openaiConfigConfirmed)
        panel_layout.addWidget(panel_label)
        panel_layout.addWidget(self.openaikey_input)
        panel_layout.addWidget(self.openaikey_button)
        panel.setLayout(panel_layout)
        return panel
    def createUserCustomonfigPanel(self):
        panel=QWidget()
        panel_layout = QVBoxLayout()
        panel_label = QLabel("请输入你的获取问答结果的代码,代码中必须使用'query'作为你的输入参数,记得代码的结尾一定要用UserCustomBot.result=''来给结果赋值,\n例如下面的列子")
        self.customcode_input = QTextEdit()
        self.customcode_input.setText("import requests\n#调用你能获取问答结果的任何代码\n\
response = requests.post(url='http://127.0.0.1:15006/ask', data=json.dumps(query))\n#记得一定要使用UserCustomBot.result=''来给结果赋值\n\
UserCustomBot.result=response.content.decode('utf8')")
        self.customcode_input.setMinimumHeight(300)
        # self.custom_button = QPushButton('确定')
        # self.custom_button.setFixedWidth(200)
        # self.custom_button.clicked.connect(self.customConfigConfirmed)
        panel_layout.addWidget(panel_label)
        panel_layout.addWidget(self.customcode_input)
        # panel_layout.addWidget(self.custom_button)
        panel.setLayout(panel_layout)
        return panel
    
        
        
    def openaiConfigConfirmed(self):
        print("openaiConfigConfirmed")
        self.chatgpt_bot=ChatGPTBot(self.openaikey_input.text())
        #self.chatgpt_bot.ask("窗前明月光")
    def customConfigConfirmed(self):
        print("customConfigConfirmed")
        self.ask("李白乘舟将欲行")
        
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
        self.move(x, y)
        self.setGeometry(x, y, 1000, 700)
        
    def ask(self,query):
        if self.ApiMode==1:
            result=self.chatgpt_bot.ask(query)
            return result
        elif  self.ApiMode==2:
            result=UserCustomBot.ask(query,self.customcode_input.toPlainText())
            print(result)
            return  result
    def clear(self):
        if self.ApiMode==1:
            result=self.chatgpt_bot.clear()
        elif  self.ApiMode==3:
          pass    
           
    
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
                self.resize(1000, 700)
            elif radioButton.text()=="你的自定义服务":
                print("你将使用你的自定义服务")
                self.openai_config.hide()
                self.usercustom_config.show()
                self.auther_config.hide()
                self.ApiMode=2
                
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
                user_data=json.loads(f.read())
                try:
                    self.username_input.setText(user_data["userid"])
                    self.password_input.setText(user_data["password"])
                    self.device_input.setText(user_data["model"])
                    self.speaker_input.setText(user_data["speakername"])
                    self.openaikey_input.setText(user_data["chatgptkey"])
                    self.customcode_input.setText(user_data["usercode"])
                    
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
        try:
            username = self.username_input.text()
            password = self.password_input.text()
            device = self.device_input.text()
            speakername=self.speaker_input.text()
            usercode=self.customcode_input.toPlainText()
            chatgptkey=self.openaikey_input.text()
            with open(os.path.join(str(Path.home()), ".michatgpt.token"),'w') as f:
                info={"userid":username,"password":password,"model":device,"speakername":speakername,"chatgptkey":chatgptkey,"usercode":usercode,"did":self.did_input.text(),
                      "tts":self.tts_input.text(),"connectmode":self.ConnectMode}
                f.write(json.dumps(info))
        except Exception as e:
            print(e)
    def on_login_button_clicked(self):
        # 在点击登录按钮时触发这个事件处理函数
        # 获取文本输入框中用户输入的内容
        self.saveconfig()
        # 在这里处理登录逻辑
        # ...
        if self.started==True:
             self.loopflag=False
        else:
            self.loopflag=True
            thread=Thread(target=self.xiaomi_thread_func)
            thread.start()
            self.started=True
            self.login_button.setText("停止")
        
    def xiaomi_thread_func(self):
        asyncio.run(self.xiaomimain())
        
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
                            

                # 找到 Intelligent_Speaker 的值和 _Play_Text 的值
                intelligent_speaker_value = d['Intelligent_Speaker']
                play_text_value = d['_Play_Text'] 
                ttscommand=intelligent_speaker_value+"-"+play_text_value
        except Exception as e:  
            print(e)
        return ttscommand
    async def xiaomimain(self):
        try:
            #-------------------------用户配置
            hardware,user_id,password=self.device_input.text(), self.username_input.text(),self.password_input.text()
            wifispeaker_name=self.speaker_input.text()
            MI_DID=""
            #---------------------------
            LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"
            COOKIE_TEMPLATE = "deviceId={device_id}; serviceToken={service_token}; userId={user_id}"
            lastTimeStamp=int(time.time()* 1000)
            async with ClientSession() as session:
                account = MiAccount(session,user_id,password,os.path.join(str(Path.home()),".mi.token"),)
                if self.ConnectMode==2:
                    ioservice = MiIOService(account)
                    deviceresult = await miio_command(ioservice, MI_DID, "list", '')
                    print(deviceresult)
                    for item in deviceresult:
                        if item["name"]==wifispeaker_name:
                            MI_DID=item["did"]
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
                deviceresult = await service.device_list()
                if not isinstance(deviceresult, str):
                    deviceid=None
                    for h in deviceresult:
                        if h.get("name", "") == wifispeaker_name:
                            deviceid = h.get("deviceID")
                    if not deviceid:
                        print("无法找到设备，已退出")
                    print("deviceid:",deviceid)
                    with open(os.path.join(str(Path.home()), ".mi.token")) as f:
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
                    print("最后的问答：",last_record)
                    self.logevent.emit(last_record)
                    if last_record and new_timestamp>lastTimeStamp:
                        self.logevent.emit("发现新消息，送往GPT请求问答")
                        await asyncio.sleep(0.5)    
                        lastTimeStamp=new_timestamp
                        if await get_if_xiaoai_is_playing():
                            await service.player_pause(deviceid)
                            await asyncio.sleep(0.5)    
                        if self.ConnectMode==1:
                           await service.text_to_speech(deviceid, '')
                        else:
                            await miio_command(ioservice, MI_DID, self.tts_input.text()+" "+"")
                        message=""
                        if "清除消息" in last_record:
                                message="GPT清除历史消息"
                                self.logevent.emit("GPT清除历史消息")
                                if self.ConnectMode==1:
                                    await service.text_to_speech(deviceid, message)
                                else:
                                    await miio_command(ioservice, MI_DID, self.tts_input.text()+" "+message)
                                
                                self.clear()
                        elif "停止" in last_record or "休息一下" in last_record:
                            self.logevent.emit("好的")
                            if self.ConnectMode==1:
                                    await service.text_to_speech(deviceid, "好的")
                            else:
                                    await miio_command(ioservice, MI_DID, self.tts_input.text()+" "+"好的")
                           
                        else:
                            if self.ConnectMode==1:
                                    await service.text_to_speech(deviceid, "正在问大哥GPT请等待")
                            else:
                                    await miio_command(ioservice, MI_DID, self.tts_input.text()+" "+"正在问大哥GPT请等待")
                            
                            gpt_result=self.ask(last_record) 
                            if gpt_result=="-1":
                                self.logevent.emit("出错了无法获取GPT消息")
                                if self.ConnectMode==1:
                                    await service.text_to_speech(deviceid, "出错了无法获取GPT消息")
                                else:
                                    await miio_command(ioservice, MI_DID, self.tts_input.text()+" "+"出错了无法获取GPT消息")
                               
                            else:
                                message+=gpt_result
                                self.logevent.emit(message)
                                if self.ConnectMode==1:
                                    await service.text_to_speech(deviceid, message)
                                else:
                                    await miio_command(ioservice, MI_DID, self.tts_input.text()+" "+message)
                              
                        
                        while True:
                            if not await get_if_xiaoai_is_playing():
                                break
                            await asyncio.sleep(0.5)
                    await asyncio.sleep(0.5)                 
        except Exception as e:
            self.logevent.emit(str(e))
            print(e)
            time.sleep(2)
            self.loopflag=True
            thread=Thread(target=self.xiaomi_thread_func)
            thread.start()
            self.started=True
            self.login_button.setText("停止")
            
        self.started=False
        print("结束小米线程")
        self.login_button.setText("开始")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    icon = QIcon('icon.png')
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())
