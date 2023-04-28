import requests
#请将url替换为你的api
url="https://service-4q4clutk-1307834456.de.apigw.tencentcs.com/release/ask?query="
url+=query
response = requests.get(url)
print(response.content.decode('utf8'))
UserCustomBot.result=response.content.decode('utf8')