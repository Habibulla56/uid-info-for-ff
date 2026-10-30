import os
import threading
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask

# ==================== Flask Server for Render Port ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "Free Fire Discord Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ==================== Discord Bot Setup ====================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ বট সফলভাবে লগইন করেছে: {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"সফলভাবে {len(synced)} টি স্ল্যাশ কমান্ড সিন্স করা হয়েছে।")
    except Exception as e:
        print(f"⚠️ কমান্ড সিন্স করতে সমস্যা হয়েছে: {e}")

# ==================== PLAYER LOOKUP COMMAND ====================
@bot.tree.command(name="player", description="Search Free Fire real player info via custom API")
@app_commands.describe(uid="Player UID")
async def player_slash(interaction: discord.Interaction, uid: str):
    await interaction.response.send_message(f"🔍 Fetching live details for UID: `{uid}` ...", ephemeral=True)
    
    target_url = f"https://auraffxserverinfocheckerapi.onrender.com/api/player?uid={uid}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url, headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    try:
                        result = await resp.json()
                    except:
                        result = {"success": False}
                else:
                    result = {"success": False}

        if result and isinstance(result, dict):
            # চেক করা যে API আসলেও প্লেয়ারের ডেটা দিয়েছে কি না
            data = result.get("data", result)
            
            # যদি এপিআই থেকে সরাসরি error বা player না পাওয়ার মেসেজ থাকে
            if "error" in result or data.get("success") == False or (isinstance(data, dict) and "error" in data):
                embed = discord.Embed(title="❌ Player Not Found", color=0xFF0000)
                embed.add_field(name="UID", value=uid, inline=False)
                embed.add_field(name="Status", value="This UID might be invalid, banned, or not found in the API database.", inline=False)
                await interaction.edit_original_response(content=None, embed=embed)
                return

            p_name = data.get("player_name", data.get("name", data.get("nickname", data.get("AccountName"))))
            p_level = data.get("level", data.get("PlayerLevel", data.get("AccountLevel", "N/A")))
            p_likes = data.get("likes", data.get("Likes", data.get("Favorable", "N/A")))
            p_guild = data.get("guild_name", data.get("guild", data.get("GuildName", "None")))
            p_region = data.get("region", data.get("Region", "BD"))

            # যদি নাম না পাওয়া যায়
            if not p_name or p_name == "Unknown":
                embed = discord.Embed(title="❌ Player Not Found", color=0xFF0000)
                embed.add_field(name="UID", value=uid, inline=False)
                embed.add_field(name="Status", value="Could not retrieve player details for this UID.", inline=False)
                await interaction.edit_original_response(content=None, embed=embed)
                return

            embed = discord.Embed(title="✅ Free Fire Player Found (API)", color=0x00FFCC)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="Name", value=f"{p_name} (Level: {p_level} - {p_region})", inline=False)
            embed.add_field(name="Likes", value=f"❤️ {p_likes}", inline=False)
