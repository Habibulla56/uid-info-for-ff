import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

# ==================== Bot Setup ====================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ বট সফলভাবে লগইন করেছে: {bot.user.name}")
    print("ফ্রি ফায়ার কাস্টম এপিআই বট প্রস্তুত!")
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
    
    # আপনার দেওয়া কাস্টম এপিআই এন্ডপয়েন্ট
    target_url = f"https://auraffxserverinfocheckerapi.onrender.com/api/player?uid={uid}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    try:
                        result = await resp.json()
                    except:
                        result = {"success": False}
                else:
                    result = {"success": False}

        # এপিআই থেকে ডাটা সফলভাবে আসলে
        if result and (result.get("success") or "player_name" in result or "name" in result or isinstance(result, dict)):
            data = result.get("data", result)
            p_name = data.get("player_name", data.get("name", "Unknown Player"))
            p_level = data.get("level", "N/A")
            p_likes = data.get("likes", "N/A")
            p_guild = data.get("guild_name", data.get("guild", "None"))
            p_region = data.get("region", "BD")

            embed = discord.Embed(title="✅ Free Fire Player Found (API)", color=0x00FFCC)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="Name", value=f"{p_name} (Level: {p_level} - {p_region})", inline=False)
            embed.add_field(name="Likes", value=f"❤️ {p_likes}", inline=False)
            embed.add_field(name="Guild Name", value=p_guild, inline=False)
            embed.set_footer(text="AuraFFX API Bot")
            
            await interaction.edit_original_response(content=None, embed=embed)
        else:
            embed = discord.Embed(title="⚠️ API Notice", color=0xF1C40F)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="Status", value="Could not fetch data or invalid UID response from API.", inline=False)
            await interaction.edit_original_response(content=None, embed=embed)

    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Connection Error: `{e}`")

# ==================== Run Bot ====================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN.strip())
else:
    print("❌ এরর: DISCORD_TOKEN এনভায়রনমেন্ট ভ্যারিয়েবল সেট করা নেই!")
