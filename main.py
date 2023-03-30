import sys
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,QRadioButton,QDesktopWidget,QTextEdit,QFrame,QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
from pathlib import Path
import os
import json
from miaccount   import   MiAccount
from minaservice import   MiNAService
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
    alert = pyqtSignal(str) # 自定义信号
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle('小米音箱服务')
        self.resize(600, 200)

        # 创建用于输入用户名、密码和设备型号的文本输入框
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.device_input = QLineEdit()

        # 将密码输入框设置为密码模式
        self.password_input.setEchoMode(QLineEdit.Password)

        # 创建用于显示标签的标签
        username_label = QLabel('你的ID:')
        password_label = QLabel('你的密码:')
        device_label = QLabel('你的设备型号:')

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
        input_layout.addWidget(self.login_button)
       
        # 创建用于显示图片的标签
        imagesize=200
        img_label = QLabel(self)
        pixmap = QPixmap('fox.png')
        pixmap = pixmap.scaledToHeight(imagesize)
        img_label.setPixmap(pixmap)
        
        service_select_box = QHBoxLayout()
        rb1 = QRadioButton('OpenAI', self)
        rb1.setChecked(True)
        service_select_box.addWidget(rb1)
        rb2 = QRadioButton('你的自定义服务', self)
        service_select_box.addWidget(rb2)
        #rb3 = QRadioButton('作者的免费测试(仅限最多50个问题)', self)
        #service_select_box.addWidget(rb3)
        service_select_box.addStretch()
        rb1.clicked.connect(self.radioClicked)
        rb2.clicked.connect(self.radioClicked)
        #rb3.clicked.connect(self.radioClicked)
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
        # image_layout.addWidget(zhifubao_label)
        #测试你的服务器
        test_label = QLabel('测试一下你的服务器')
        testServiceLayout=QVBoxLayout()
        self.askresult = QTextEdit()
        self.testAsk=QLineEdit()
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        testServiceLayout.addWidget(line)
        testServiceLayout.addWidget(test_label)
        testServiceLayout.addWidget(self.askresult)
        askLayout=QHBoxLayout()
        askLayout.addWidget( self.testAsk)
        self.testAskSend=QPushButton("发送")
        askLayout.addWidget( self.testAskSend)
        self.testAskSend.clicked.connect(self.on_testAskSend_clicked)
        testServiceLayout.addLayout(askLayout)
        
        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addLayout(service_select_box)
        layout.addLayout(service_config_box)
        layout.addLayout(image_layout)
        layout.addLayout(testServiceLayout)
        layout.addStretch()
        
        # 设置该窗口的布局器为垂直布局器
        self.setLayout(layout)
       
        self.readUserInfo()
        self.loopflag=True
        self.started=False
        self.center_window()
        self.ApiMode=1 #1 openapi 2 自定义服务 3 作者的测试服务器
        self.chatgpt_bot=ChatGPTBot(self.openaikey_input.text())
        self.alert.connect(self.deviceInvalid) #
    
    
    def on_testAskSend_clicked(self):
        if(self.testAsk.text()!=""):
            print(self.testAsk.text())
            result=self.ask(self.testAsk.text())
            self.askresult.setText(result)
            self.testAsk.setText("")
                        
        
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
        self.setGeometry(x, y, 900, 400)
        
    def ask(self,query):
        if self.ApiMode==1:
            result=self.chatgpt_bot.ask(query)
        elif  self.ApiMode==2:
            result=UserCustomBot.ask(query,self.customcode_input.toPlainText())
            print(result)
            return result
    def clear(self):
        if self.ApiMode==1:
            result=self.chatgpt_bot.clear()
        elif  self.ApiMode==3:
          pass    
           
        
    def radioClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.text()=="OpenAI":
                print("你将直接调用openai服务")
                self.openai_config.show()
                self.usercustom_config.hide()
                self.auther_config.hide()
                self.ApiMode=1
                self.resize(900, 500)
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
                self.resize(900, 400)
                
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
                except Exception as e:
                    print(e)
            
    def on_login_button_clicked(self):
        # 在点击登录按钮时触发这个事件处理函数
        # 获取文本输入框中用户输入的内容
        try:
            username = self.username_input.text()
            password = self.password_input.text()
            device = self.device_input.text()
            speakername=self.speaker_input.text()
            usercode=self.customcode_input.toPlainText()
            chatgptkey=self.openaikey_input.text()
            with open(os.path.join(str(Path.home()), ".michatgpt.token"),'w') as f:
                info={"userid":username,"password":password,"model":device,"speakername":speakername,"chatgptkey":chatgptkey,"usercode":usercode}
                f.write(json.dumps(info))
        except Exception as e:
            print(e)
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
        
    async def xiaomimain(self):
        try:
            #-------------------------用户配置
            hardware,user_id,password=self.device_input.text(), self.username_input.text(),self.password_input.text()
            wifispeaker_name=self.speaker_input.text()
            #---------------------------
            LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"
            COOKIE_TEMPLATE = "deviceId={device_id}; serviceToken={service_token}; userId={user_id}"
            lastTimeStamp=int(time.time()* 1000)
            async with ClientSession() as session:
                account = MiAccount(session,user_id,password,os.path.join(str(Path.home()),".mi.token"),)
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
                    if last_record and new_timestamp>lastTimeStamp:
                        await asyncio.sleep(0.5)    
                        lastTimeStamp=new_timestamp
                        if await get_if_xiaoai_is_playing():
                            await service.player_pause(deviceid)
                            await asyncio.sleep(0.5)    
                        await service.text_to_speech(deviceid, '')
                        message=""
                        if "清除消息" in last_record:
                                message="GPT 清除历史消息"
                                await service.text_to_speech(deviceid, message)
                                self.clear()
                        elif "停止" in last_record or "休息一下" in last_record:
                             await service.text_to_speech(deviceid, "好的")
                        else:
                            message+=self.ask(last_record)  
                            await service.text_to_speech(deviceid, message)
                        
                        while True:
                            if not await get_if_xiaoai_is_playing():
                                break
                            await asyncio.sleep(0.5)
                    await asyncio.sleep(0.5)                 
        except Exception as e:
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
