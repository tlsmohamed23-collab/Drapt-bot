import os
import discord
from discord.ext import commands
from discord import app_commands
import datetime

intents = discord.Intents.default()
intents.members = True  # مطلوب لتفعيل صلاحيات الأعضاء

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()

# أمر الطرد (Kick)
@bot.tree.command(name="kick", description="طرد عضو من السيرفر")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ تم طرد {member.mention} | السبب: {reason}")

# أمر الحظر (Ban)
@bot.tree.command(name="ban", description="حظر عضو من السيرفر")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ تم حظر {member.mention} | السبب: {reason}")

# أمر العزل المؤقت (Timeout)
@bot.tree.command(name="timeout", description="إعطاء عزل مؤقت لعضو بالدقائق")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "لا يوجد سبب"):
    duration = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"⏰ تم عزل {member.mention} لمدة {minutes} دقيقة | السبب: {reason}")

# تشغيل البوت باستخدام التوكن (س نقوم بإضافته في إعدادات Render لاحقاً بأمان)
bot.run(os.getenv('DISCORD_TOKEN'))
from flask import Flask
from threading import Thread
import os
import discord
from discord.ext import commands

# إنشاء خادم ويب وهمي لإبقاء الخدمة نشطة على Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# إعدادات البوت الخاص بك
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(fLogged in as {bot.user})

# تشغيل الخادم الوهمي ثم تشغيل البوت
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
