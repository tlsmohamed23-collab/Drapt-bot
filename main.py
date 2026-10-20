import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands

# ---------------------------------------------------------
# ضع رقم سيرفرك (Server ID / Guild ID) هنا بين الأقواس
# مثال: GUILD_ID = discord.Object(id=123456789012345678)
GUILD_ID = discord.Object(id=ضع_رقم_السيرفر_هنا)
# ---------------------------------------------------------

# خادم Flask لإبقاء البوت متصلاً 24/7
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
    # مزامنة الأوامر مع سيرفرك فوراً
    bot.tree.copy_global_to(guild=GUILD_ID)
    await bot.tree.sync(guild=GUILD_ID)
    print(f"Logged in as {bot.user} - Commands synced successfully!")

# --- أمثلة على أوامر السلاش (Slash Commands) ---

# أمر طرد (Kick)
@bot.tree.command(name="kick", description="طرد عضو من السيرفر")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ تم طرد {member.mention} | السبب: {reason}")

# أمر حظر (Ban)
@bot.tree.command(name="ban", description="حظر عضو من السيرفر")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ تم حظر {member.mention} | السبب: {reason}")

keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
