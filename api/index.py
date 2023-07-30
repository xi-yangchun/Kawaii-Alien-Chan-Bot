# インストールした discord.py を読み込む
import discord
import requests
import json
import os

from flask import Flask
from threading import Thread

class Alien_Chan:
    def __init__(self,json_pref):
        with open(json_pref,'r') as f:
            self.settings=json.load(f)
        self.discord_token=os.getenv("DISCORD_TOKEN")
        self.gpt_api_key=os.getenv("CHATGPT_APIKEY")
        self.kill_code=os.getenv("KILL_CODE")
        with open(self.settings['roleplay'], 'r') as f:
            self.roleplay=f.read()
            self.roleplay=self.roleplay.replace("XXXXXX",self.kill_code)

        self.header={
            "Content-Type":"application/json",
            "Authorization":f"Bearer {self.gpt_api_key}",
        }
        self.body={
            "model":"gpt-3.5-turbo",
            "messages": [{"role":"system","content":self.roleplay}]
        }
        with open(self.settings['pretalk']) as f:
            pretj=json.load(f)
        self.len_pretalks=len(pretj['talks'])
        for talk in pretj['talks']:
            self.body["messages"].append(talk)
        self.prefix=self.settings["prefix"]
    
    def run(self):
        # 接続に必要なオブジェクトを生成
        Intents = discord.Intents.all()
        Intents.members = True
        client = discord.Client(intents=Intents)

        # 起動時に動作する処理
        @client.event
        async def on_ready():
            # 起動したらターミナルにログイン通知が表示される
            print('logged in')

        # メッセージ受信時に動作する処理
        @client.event
        async def on_message(message):
            # メッセージ送信者がBotだった場合は無視する
            if message.author.bot:
                return
            
            if message.content[0:len(list(self.prefix))]==self.prefix:
                question=message.content.replace('/gpt ','')
                if len(self.body["messages"])>=100:
                    self.body["messages"].pop(self.len_pretalks)
                self.body["messages"].append(
                    {"role":"user","content":question}
                )
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions", 
                    headers = self.header, data = json.dumps(self.body)
                    .encode('utf_8'))
                answer=response.json()["choices"][0]["message"]['content']
                self.body["messages"]\
                .append(response.json()["choices"][0]["message"])
                #print(self.body["messages"])
                #print(len(self.body["messages"]))
                await message.channel.send(answer)

        # Botの起動とDiscordサーバーへの接続
        try:
            client.run(self.discord_token)
        except:
            os.system("kill 1")

bot=Alien_Chan("settings.json")
t = Thread(target=bot.run)
t.start()

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"
