import os
import threading
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request, jsonify

# ==================== Flask Server for Render ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "Free Fire Discord Bot & Profile Stats API is Alive!"

@app.route('/api/player', methods=['GET'])
def web_player_api():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"success": False, "error": "UID is required"})
    return jsonify({"success": True, "uid": uid, "status": "API Endpoint Active"})

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
@bot.tree.command(name="player", description="Check Free Fire Profile Stats and Account Info")
@app_commands.describe(uid="Player UID")
async def player_slash(interaction: discord.Interaction, uid: str):
    await interaction.response.send_message(f"🔍 Fetching details for UID: `{uid}` ...", ephemeral=True)
    
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
            data = result.get("data", result)
            
            # এরর চেক
            if "error" in result or data.get("success") == False or (isinstance(data, dict) and "error" in data):
                embed = discord.Embed(title="❌ Profile Not Found", color=0xFF0000)
                embed.add_field(name="UID", value=uid, inline=False)
                embed.add_field(name="Status", value="This UID is invalid, banned, or not found in the database.", inline=False)
                await interaction.edit_original_response(content=None, embed=embed)
                return

            # ডাটা এক্সট্রাকশন (নিরাপদভাবে ডিকশনারি ফিল্ড চেক)
            p_name = data.get("player_name", data.get("name", data.get("nickname", data.get("AccountName"))))
            p_level = data.get("level", data.get("PlayerLevel", data.get("AccountLevel", "N/A")))
            p_likes = data.get("likes", data.get("Likes", data.get("Favorable", "N/A")))
            p_guild = data.get("guild_name", data.get("guild", data.get("GuildName", "None")))
            p_region = data.get("region", data.get("Region", "BD"))
            
            # এক্সট্রা গেম স্ট্যাটস (এপিআই সাপোর্ট করলে দেখাবে, না থাকলে N/A দেখাবে)
            p_br_rank = data.get("br_rank", data.get("BRRank", data.get("rank", "N/A")))
            p_cs_rank = data.get("cs_rank", data.get("CSRank", "N/A"))
            p_create_date = data.get("create_time", data.get("AccountCreateTime", data.get("creation_date", "N/A")))

            if not p_name or p_name == "Unknown":
                embed = discord.Embed(title="❌ Profile Not Found", color=0xFF0000)
                embed.add_field(name="UID", value=uid, inline=False)
                embed.add_field(name="Status", value="Could not retrieve profile stats for this UID.", inline=False)
                await interaction.edit_original_response(content=None, embed=embed)
                return

            # ডিসকর্ড এম্বেড রেসপন্স
            embed = discord.Embed(title="🎮 Free Fire Player Profile Stats", color=0x00FFCC)
            embed.add_field(name="👤 Player Name", value=str(p_name), inline=True)
            embed.add_field(name="🆔 UID", value=str(uid), inline=True)
            embed.add_field(name="⭐ Level", value=str(p_level), inline=True)
            embed.add_field(name="🌍 Region", value=str(p_region), inline=True)
            embed.add_field(name="❤️ Likes", value=str(p_likes), inline=True)
            embed.add_field(name="🛡️ Guild Name", value=str(p_guild), inline=True)
            embed.add_field(name="🏆 BR Rank", value=str(p_br_rank), inline=True)
            embed.add_field(name="⚔️ CS Rank", value=str(p_cs_rank), inline=True)
            embed.add_field(name="📅 Creation Date", value=str(p_create_date), inline=False)
            embed.set_footer(text="AuraFFX Profile Bot • Powered by Custom API")
            
            await interaction.edit_original_response(content=None, embed=embed)
        else:
            embed = discord.Embed(title="⚠️ API Notice", color=0xF1C40F)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="Status", value="Failed to fetch profile data from API server.", inline=False)
            await interaction.edit_original_response(content=None, embed=embed)

    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Connection Error: `{e}`")

# ==================== Run Flask & Bot ====================
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN.strip())
    else:
        print("❌ এরর: DISCORD_TOKEN এনভায়রনমেন্ট ভ্যারিয়েবল সেট করা নেই!")
