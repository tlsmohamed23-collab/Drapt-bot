import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# خادم وهمي لإبقاء البوت متصلاً
app = Flask('')

@app.route('/')
def home():
    return "Bot is active!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
