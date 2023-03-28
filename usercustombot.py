import requests
import json
class UserCustomBot():
    result=""
    @classmethod
    def ask(cls,query,user_code):
        try:
            exec(user_code)
            return UserCustomBot.result
        except Exception as e:
            return "-1"
  