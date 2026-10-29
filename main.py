import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from bs4 import BeautifulSoup

# ==================== Bot Setup ====================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# ==================== PLAYER LOOKUP COMMAND ====================
@bot.tree.command(name="player", description="Search Free Fire real player info via live backend")
@app_commands.describe(uid="Player UID")
async def player_slash(interaction: discord.Interaction, uid: str):
    await interaction.response.send_message(f"🔍 Fetching live details for UID: `{uid}` ...", ephemeral=True)
    
    # Target live endpoint/website request simulation
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

        if result.get("success") or isinstance(result, dict) and "player_name" in result:
            data = result.get("data", result)
            p_name = data.get("player_name", data.get("name", "Unknown Player"))
            p_level = data.get("level", "N/A")
            p_likes = data.get("likes", "N/A")
            p_guild = data.get("guild_name", "None")
            p_region = data.get("region", "BD")

            embed = discord.Embed(title="✅ Live Free Fire Player Found!", color=0x00FFCC)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="Name", value=f"{p_name} (Level: {p_level} - {p_region})", inline=False)
            embed.add_field(name="Likes", value=f"❤️ {p_likes}", inline=False)
            embed.add_field(name="Guild Name", value=p_guild, inline=False)
            
            await interaction.edit_original_response(content=None, embed=embed)
        else:
            embed = discord.Embed(title="⚠️ Live Fetch Notice", color=0xF1C40F)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="Status", value="Live backend security (Cloudflare/Anti-bot) detected or direct lookup restricted.", inline=False)
            embed.set_footer(text="Please use manual verification or authorized gateway.")
            await interaction.edit_original_response(content=None, embed=embed)

    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Connection or Security Block Error: `{e}`")

# ==================== Run Bot ====================
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN.strip())
else:
    print("❌ Error: DISCORD_TOKEN environment variable not set!")
