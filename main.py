# インストールした discord.py を読み込む
import discord
from openai import OpenAI
import json
import os

class Alien_Chan:
    def __init__(self,json_pref):
        with open(json_pref,'r') as f:
            self.settings=json.load(f)
        self.discord_token=os.getenv("ALIEN_TOKEN")
        with open(self.settings['roleplay'], 'r') as f:
            self.roleplay=f.read()
        self.killcode=os.getenv("ALIEN_KILLCODE")

        self.messages=[]
        self.messages.append({"role":"system","content":self.roleplay})
        with open(self.settings['pretalk'],"r") as f:
            self.pretalk=json.load(f)["talks"]
        self.len_pretalks=len(self.pretalk)
        self.messages=self.messages+self.pretalk
        self.gpt_client=OpenAI(api_key=os.getenv("ALIEN_APIKEY"))
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
                question=message.content.replace(self.prefix,'')
                if len(self.messages)>=100:
                    self.messages.pop(self.len_pretalks)
                self.messages.append(
                    {"role":"user","content":question}
                )
                completion = self.gpt_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=self.messages
                )
                answer=completion.choices[0].message.content
                answer_=completion.choices[0].message
                self.messages\
                .append({"role":answer_.role,"content":answer_.content})
                #print(self.body["messages"])
                #print(len(self.body["messages"]))
                await message.channel.send(answer)

        # Botの起動とDiscordサーバーへの接続
        try:
            client.run(self.discord_token)
        except:
            os.system("kill 1")

bot=Alien_Chan("settings.json")
bot.run()
