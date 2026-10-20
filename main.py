import os
import random
import json
import urllib.request
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands

# ---------------------------------------------------------
# رقم سيرفرك الخاص (Guild ID)
GUILD_ID = discord.Object(id=1524150798458818821)
# ---------------------------------------------------------

app = Flask('')

@app.route('/')
def home():
    return "Bot is active 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    bot.tree.copy_global_to(guild=GUILD_ID)
    await bot.tree.sync(guild=GUILD_ID)
    print(f"Logged in as {bot.user} - All commands synced successfully!")

# ==========================================
# 🧠 1. أمر الذكاء الاصطناعي المنطقي (AI Smart Assistant)
# ==========================================

@bot.tree.command(name="ai", description="اطرح أي سؤال على الذكاء الاصطناعي وسيجيبك بتحليل منطقي وذكي")
async def ai_cmd(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            # تعليمات وتوجيه الذكاء الاصطناعي للرد بأسلوب منطقي، عقلاني، وواضح
            system_prompt = (
                "أنت مساعد ذكاء اصطناعي منطقي وذكي ومحترف في سيرفر ديسكورد. "
                "أجب عن جميع الأسئلة بأسلوب عقلاني، تحليلي، ومفهوم بوضوح. "
                "إذا كان السؤال عن صانعك، فأوضح أنك بوت تم تطويره بواسطة moha11dz. "
                "اجعل إجاباتك جادة ومفيدة ودقيقة دون كلام عشوائي، واحرص على ألا تتجاوز الإجابة فقرة واحدة أو فقرتين قصيرتين."
            )
            
            full_prompt = f"{system_prompt}\n\nسؤال المستخدم: {question}"
            
            data = json.dumps({"contents": [{"parts": [{"text": full_prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                ai_reply = result['candidates'][0]['content']['parts'][0]['text']
                
                embed = discord.Embed(
                    title="🧠 إجابة الذكاء الاصطناعي",
                    description=ai_reply,
                    color=discord.Color.blue()
                )
                embed.add_field(name="❓ السؤال المطروح", value=question, inline=False)
                embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
                
                await interaction.followup.send(embed=embed)
                return
        except Exception as e:
            print(f"AI Error: {e}")

    await interaction.followup.send("⚠️ تعذر الاتصال بمحرك الذكاء الاصطناعي. تأكد من ضبط مفتاح `GEMINI_API_KEY` في إعدادات Render.")

# أمر 8ball المنطقي للتوافق مع الأمر القديم
@bot.tree.command(name="8ball", description="اسأل الذكاء الاصطناعي سؤالاً منطقياً")
async def ball(interaction: discord.Interaction, question: str):
    await ai_cmd(interaction, question)

# ==========================================
# 🛡️ 2. أوامر الإشراف والتنظيم (Admin & Mod)
# ==========================================

@bot.tree.command(name="kick", description="طرد عضو من السيرفر")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    await interaction.response.defer()
    await member.kick(reason=reason)
    await interaction.followup.send(f"✅ تم طرد {member.mention} | السبب: {reason}")

@bot.tree.command(name="ban", description="حظر عضو من السيرفر")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    await interaction.response.defer()
    await member.ban(reason=reason)
    await interaction.followup.send(f"⛔ تم حظر {member.mention} | السبب: {reason}")

@bot.tree.command(name="clear", description="مسح عدد محدد من الرسائل")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 تم مسح {len(deleted)} رسالة بنجاح.")

@bot.tree.command(name="mute", description="كتم عضو لمدة محددة بالدقائق")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "لا يوجد"):
    await interaction.response.defer()
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.followup.send(f"🤫 تم كتم {member.mention} لمدة {minutes} دقيقة.")

@bot.tree.command(name="unmute", description="إلغاء الكتم عن عضو")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    await member.timeout(None)
    await interaction.followup.send(f"🔊 تم إلغاء الكتم عن {member.mention}")

@bot.tree.command(name="lock", description="قفل الروم الحالي")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.followup.send("🔒 تم قفل الروم.")

@bot.tree.command(name="unlock", description="فتح الروم الحالي")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.followup.send("🔓 تم فتح الروم.")

# ==========================================
# 📊 3. أوامر المعلومات والخدمات (Info & Utilities)
# ==========================================

@bot.tree.command(name="ping", description="عرض سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    await interaction.response.defer()
    latency = round(bot.latency * 1000)
    await interaction.followup.send(f"🏓 Pong! السرعة: **{latency}ms**")

@bot.tree.command(name="userinfo", description="عرض معلومات عن عضو محدد")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer()
    member = member or interaction.user
    embed = discord.Embed(title=f"معلومات {member.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="الـ ID", value=member.id, inline=True)
    embed.add_field(name="تاريخ الانضمام للديسكورد", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="تاريخ الانضمام للسيرفر", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="serverinfo", description="عرض معلومات عن السيرفر")
async def serverinfo(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild
    embed = discord.Embed(title=f"معلومات سيرفر {guild.name}", color=discord.Color.green())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="مالك السيرفر", value=guild.owner.mention, inline=True)
    embed.add_field(name="عدد الأعضاء", value=guild.member_count, inline=True)
    embed.add_field(name="عدد الرومات", value=len(guild.channels), inline=True)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="avatar", description="عرض صورة الحساب الخاصة بعضو")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer()
    member = member or interaction.user
    embed = discord.Embed(title=f"صورة {member.name}", color=discord.Color.random())
    embed.set_image(url=member.display_avatar.url)
    await interaction.followup.send(embed=embed)

# تشغيل خادم Flask ثم البوت
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
