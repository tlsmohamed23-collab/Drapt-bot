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
# رقم سيرفرك الخاص (Guild ID) مضاف ومثبت جاهزاً
GUILD_ID = discord.Object(id=1524150798458818821)
# ---------------------------------------------------------

# خادم Flask لإبقاء البوت متصلاً 24/7 على Render
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
# 🤖 1. أمر الذكاء الاصطناعي (AI Smart Command)
# ==========================================

@bot.tree.command(name="8ball", description="اسأل الذكاء الاصطناعي أي سؤال وسيجيبك بدقة")
async def ball(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # استخدام Gemini API إذا كان مفتاح الـ API مضافاً في Render
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            prompt = f"أنت مساعد ذكي ولطيف في ديسكورد للبوت Drapt Bot. أجب عن هذا السؤال بأسلوب مختصر ومفيد (لا تتجاوز 3 جمل): {question}"
            
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                ai_reply = result['candidates'][0]['content']['parts'][0]['text']
                await interaction.followup.send(f"❓ **السؤال:** {question}\n🤖 **الذكاء الاصطناعي:**\n{ai_reply}")
                return
        except Exception as e:
            print(f"AI Error: {e}")

    # إجابة احتياطية ذكية في حال عدم إضافة مفتاح الـ API بعد
    responses = [
        "نعم، بالتأكيد!",
        "لا أعتقد ذلك.",
        "من المحتمل جداً.",
        "تم إنشائي وتطويري بواسطة المطور المحترف moha11dz!",
        "سؤال رائع! الإجابة تعتمد على كيفية رؤيتك للأمر."
    ]
    reply = random.choice(responses)
    await interaction.followup.send(f"❓ **السؤال:** {question}\n🔮 **الإجابة:** {reply}")

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

@bot.tree.command(name="unban", description="إلغاء حظر عضو (باستخدام ID)")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    await interaction.response.defer()
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.followup.send(f"🔓 تم إلغاء حظر {user.name}")

@bot.tree.command(name="clear", description="مسح عدد محدد من الرسائل")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 تم مسح {len(deleted)} رسالة بنجاح.")

@bot.tree.command(name="mute", description="كتم عضو (Timeout) لمدة محددة بالدقائق")
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

@bot.tree.command(name="nick", description="تغيير اسم عضو داخل السيرفر")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def nick(interaction: discord.Interaction, member: discord.Member, new_nickname: str):
    await interaction.response.defer()
    await member.edit(nick=new_nickname)
    await interaction.followup.send(f"✏️ تم تغيير اسم {member.mention} إلى: **{new_nickname}**")

@bot.tree.command(name="slowmode", description="تحديد وضع التبطئ في الروم (بالثواني)")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.response.defer()
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.followup.send(f"⏱️ تم ضبط وضع التبطيء إلى {seconds} ثانية.")

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
# 📊 3. أوامر المعلومات (Info & Stats)
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

@bot.tree.command(name="botinfo", description="معلومات سريعة عن البوت")
async def botinfo(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(f"🤖 أنا بوت شغال على Render بحالة ممتازة ومتصل بـ {len(bot.guilds)} سيرفر!")

# ==========================================
# 🎲 4. أوامر التسلية والترفيه (Fun)
# ==========================================

@bot.tree.command(name="roll", description="رمي نرد من 1 إلى 6 (أو أي رقم تحدده)")
async def roll(interaction: discord.Interaction, max_number: int = 6):
    await interaction.response.defer()
    result = random.randint(1, max_number)
    await interaction.followup.send(f"🎲 النتيجة هي: **{result}**")

@bot.tree.command(name="coinflip", description="رمي عملة نقدية (ملك أو كتابة)")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.defer()
    result = random.choice(["👑 ملك (Heads)", "📜 كتابة (Tails)"])
    await interaction.followup.send(f"🪙 النتيجة: **{result}**")

@bot.tree.command(name="rps", description="لعبة حجر ورقة مقص")
async def rps(interaction: discord.Interaction, choice: str):
    await interaction.response.defer()
    options = ["حجر", "ورقة", "مقص"]
    bot_choice = random.choice(options)
    await interaction.followup.send(f"أنت اخترت: **{choice}** | البوت اختار: **{bot_choice}**")

@bot.tree.command(name="roast", description="قصف جبهة عشوائي لطيف")
async def roast(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    roasts = [
        "عقلك مثل الصفحة الرئيسية في الـ 404... غير موجود!",
        "أنت السبب الرئيسي في وضع تحذيرات على العلب الفاضية.",
        "لو كان الهبل رياضة كنت أخذت الميدالية الذهبية!"
    ]
    await interaction.followup.send(f"{member.mention} {random.choice(roasts)}")

@bot.tree.command(name="rate", description="تقييم أي شيء من 100%")
async def rate(interaction: discord.Interaction, thing: str):
    await interaction.response.defer()
    score = random.randint(0, 100)
    await interaction.followup.send(f"📊 تقييمي لـ **{thing}** هو: **{score}%**")

@bot.tree.command(name="ship", description="حساب نسبة التوافق بين شخصين")
async def ship(interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
    await interaction.response.defer()
    percentage = random.randint(0, 100)
    await interaction.followup.send(f"❤️ نسبة التوافق بين {user1.mention} و {user2.mention} هي: **{percentage}%**")

# ==========================================
# 🛠️ 5. أدوات عامة وأوامر خفيفة (Utilities & Misc)
# ==========================================

@bot.tree.command(name="say", description="جعل البوت يكرر كلامك")
async def say(interaction: discord.Interaction, text: str):
    await interaction.response.send_message("تم الإرسال!", ephemeral=True)
    await interaction.channel.send(text)

@bot.tree.command(name="embed", description="إرسال رسالة منسقة داخل إطار (Embed)")
async def embed_cmd(interaction: discord.Interaction, title: str, description: str):
    await interaction.response.defer()
    embed = discord.Embed(title=title, description=description, color=discord.Color.gold())
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="poll", description="عمل تصويت سريع (نعم / لا)")
async def poll(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    embed = discord.Embed(title="📊 تصويت جديد", description=question, color=discord.Color.purple())
    embed.set_footer(text=f"بواسطة: {interaction.user.name}")
    await interaction.followup.send(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.tree.command(name="math", description="آلة حاسبة بسيطة (+, -, *, /)")
async def math_cmd(interaction: discord.Interaction, num1: float, operation: str, num2: float):
    await interaction.response.defer()
    if operation == "+": res = num1 + num2
    elif operation == "-": res = num1 - num2
    elif operation == "*": res = num1 * num2
    elif operation == "/": res = num1 / num2 if num2 != 0 else "لا يمكن القسمة على صفر"
    else: res = "عملية غير معروفة"
    await interaction.followup.send(f"🧮 النتيجة: **{res}**")

@bot.tree.command(name="choose", description="دع البوت يختار لك بين خيارين أو أكثر (افصل بينهم بفاصلة)")
async def choose(interaction: discord.Interaction, choices: str):
    await interaction.response.defer()
    options = choices.split(",")
    selection = random.choice(options).strip()
    await interaction.followup.send(f"🤔 اختياري لك هو: **{selection}**")

@bot.tree.command(name="reverse", description="عكس النص المكتوب")
async def reverse(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    await interaction.followup.send(f"🔄 العكس: `{text[::-1]}`")

@bot.tree.command(name="uppercase", description="تحويل النص إلى حروف كبيرة (للإنجليزية)")
async def uppercase(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    await interaction.followup.send(f"🔠 `{text.upper()}`")

@bot.tree.command(name="remind", description="تذكيرك بأمر ما بعد دقائق معدودة")
async def remind(interaction: discord.Interaction, minutes: int, reminder: str):
    await interaction.response.defer()
    await interaction.followup.send(f"⏰ حُفظ التذكير! سأذكرك بـ '{reminder}' بعد {minutes} دقيقة.")
    import asyncio
    await asyncio.sleep(minutes * 60)
    await interaction.followup.send(f"🔔 {interaction.user.mention} تذكير: **{reminder}**")

@bot.tree.command(name="invite", description="رابط دعوة البوت لسيرفرات أخرى")
async def invite(interaction: discord.Interaction):
    await interaction.response.defer()
    link = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    await interaction.followup.send(f"🔗 يمكنك دعوة البوت عبر هذا الرابط:\n{link}")

# تشغيل خادم Flask ثم البوت
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
