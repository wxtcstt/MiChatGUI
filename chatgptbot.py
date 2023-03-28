import openai
class ChatGPTBot():
    def __init__(self, openai_key, api_base=None):
        self.history = []
        self.api_base = api_base
        self.openai_key = openai_key
    def clear(self):
        self.history=[]
    def ask(self, query):
        try:
            openai.api_key = self.openai_key
            if self.api_base:
                openai.api_base = self.api_base
            ms = []
            for h in self.history:
                ms.append({"role": "user", "content": h[0]})
                ms.append({"role": "assistant", "content": h[1]})
            ms.append({"role": "user", "content": f"{query}"})
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=ms)
            message = (
                completion["choices"][0]
                .get("message")
                .get("content")
                .encode("utf8")
                .decode()
            )
            self.history.append([f"{query}", message])
            self.history = self.history[-5:]
            return message
        except Exception as e:
            return "-1"
