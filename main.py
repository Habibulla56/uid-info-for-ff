import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from bs4 import BeautifulSoup

# ডিসকর্ড বট টোকেন (Render এনভায়রনমেন্ট ভ্যারিয়েবল থেকে রিড করবে)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# ডিসকর্ড বট ইন্টেন্টস কনফিগারেশন
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ বট সফলভাবে লগইন করেছে: {bot.user.name}")
    print("ফ্রি ফায়ার ইউআইডি চেকার বট প্রস্তুত!")
    try:
        synced = await bot.tree.sync()
        print(f"সফলভাবে {len(synced)} টি স্ল্যাশ কমান্ড সিন্স করা হয়েছে।")
    except Exception as e:
        print(f"⚠️ কমান্ড সিন্স করতে সমস্যা হয়েছে: {e}")

# ==================== PLAYER LOOKUP COMMAND ====================
@bot.tree.command(name="player", description="ফ্রি ফায়ার প্লেয়ারের রিয়েল ইন-গেম তথ্য সার্চ করুন")
@app_commands.describe(uid="প্লেয়ারের ইউআইডি (UID) লিখুন")
async def player_slash(interaction: discord.Interaction, uid: str):
    await interaction.response.send_message(f"🔍 ইউআইডি `{uid}` এর তথ্য খোঁজা হচ্ছে...", ephemeral=True)
    
    # লাইভ ব্যাকএন্ড বা টপআপ সাইট রিকোয়েস্ট লিংক
    target_url = f"https://munnatopup.com/api/check?uid={uid}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://munnatopup.com/"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    try:
                        result = await resp.json()
                    except:
                        text_data = await resp.text()
                        soup = BeautifulSoup(text_data, 'html.parser')
                        result = {"success": False}
                else:
                    result = {"success": False}

        # যদি ডাটা সফলভাবে পাওয়া যায়
        if result.get("success") or isinstance(result, dict) and "player_name" in result:
            data = result.get("data", result)
            p_name = data.get("player_name", data.get("name", "অজানা প্লেয়ার"))
            p_level = data.get("level", "N/A")
            p_likes = data.get("likes", "N/A")
            p_guild = data.get("guild_name", "নেই")
            p_region = data.get("region", "BD")

            embed = discord.Embed(title="✅ ফ্রি ফায়ার প্লেয়ার প্রফাইল পাওয়া গেছে!", color=0x00FFCC)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="নাম ও লেভেল", value=f"{p_name} (লেভেল: {p_level} - {p_region})", inline=False)
            embed.add_field(name="মোট লাইক", value=f"❤️ {p_likes}", inline=False)
            embed.add_field(name="গিল্ডের নাম", value=p_guild, inline=False)
            embed.set_footer(text="Habibulla Gaming Security Bot")
            
            await interaction.edit_original_response(content=None, embed=embed)
        else:
            # ক্লাউডফ্লায়ার বা সিকিউরিটি ব্লক হ্যান্ডেল করার নোটিশ
            embed = discord.Embed(title="⚠️ লাইভ ডাটা নোটিশ", color=0xF1C40F)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="স্ট্যাটাস", value="টার্গেট সার্ভারে সিকিউরিটি ব্লক (Cloudflare/Anti-bot) রয়েছে, তাই ডাইরেক্ট ফেচ করা যাচ্ছে না।", inline=False)
            embed.set_footer(text="Habibulla Gaming Security Bot")
            await interaction.edit_original_response(content=None, embed=embed)

    except Exception as e:
        await interaction.edit_original_response(content=f"❌ কানেকশন বা সিকিউরিটি এরর: `{e}`")

# বট রান করা
if DISCORD_BOT_TOKEN:
    bot.run(DISCORD_BOT_TOKEN.strip())
else:
    print("❌ এরর: DISCORD_TOKEN এনভায়রনমেন্ট ভ্যারিয়েবল সেট করা নেই!")
