import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

GUILD_ID = discord.Object(id=ضع_رقم_السيرفر_هنا)

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
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    bot.tree.copy_global_to(guild=GUILD_ID)
    await bot.tree.sync(guild=GUILD_ID)
    print(f"Logged in as {bot.user} - Ready!")

@bot.tree.command(name="ping", description="اختبار سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    # 1. إخبار ديسكورد فوراً بأن البوت يعمل على الطلب لمنع ظهور خطأ التطبيق لم يستجب
    await interaction.response.defer(ephemeral=False)
    
    # 2. إرسال النتيجة الفعلية باستخدام followup بدلاً من response العادية
    latency = round(bot.latency * 1000)
    await interaction.followup.send(f"pong! 🏓 السرعة: **{latency}ms**")

keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
