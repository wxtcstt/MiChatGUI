from flask import Flask,request

opeailoaded="0"
try:
   import openai
   #修改下面的api——key为你的key
   openai.api_key = "sk-*************************"
   opeailoaded="1"
except Exception as e:
   opeailoaded="0"

app = Flask(__name__)

@app.route('/')
def hello_world():
   if opeailoaded=="1":
      return 'openailoaded'
   else:
      return "openai not loaded"

@app.route('/ask')
def ask():
   try:
      query=request.args.get("query")
      response=openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},

         ]
      )
      return response["choices"][0]["message"]["content"]
   except Exception as e:
      print(str(e))
      return "无法获取结果"
if __name__ == '__main__':
   app.run(host='0.0.0.0',port=9000)