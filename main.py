import sys
import os

# Render এবং লোকাল সার্ভারের জন্য পাইথন পাথ ফিক্সার
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import threading
import json
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request, jsonify
from flask_cors import CORS

# ব্যাকএন্ড মডিউলগুলো ইমপোর্ট
from Utilities.until import load_accounts
from Api.Account import get_garena_token, get_major_login
from Api.InGame import get_player_personal_show, get_player_stats, search_account_by_keyword

# একাউন্ট লোড করা
accounts = load_accounts()

# ==================== Flask App & API Routes ====================
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Free Fire Bot & Full Stats API is Alive!"

@app.route('/get_player_personal_show', methods=['GET'])
def get_account_info():
    try:
        server = request.args.get('server', 'BD').upper()
        uid = request.args.get('uid')
        need_gallery_info = request.args.get('need_gallery_info', False)
        need_blacklist = request.args.get('need_blacklist', False)
        need_spark_info = request.args.get('need_spark_info', False)
        call_sign_src = request.args.get('call_sign_src', 7)
        
        if not uid or not uid.isdigit():
            return jsonify({"status": "error", "message": "Valid numeric UID is required"}), 400

        if server not in accounts:
            server = list(accounts.keys())[0]

        garena_token_result = get_garena_token(accounts[server]['uid'], accounts[server]['password'])
        if not garena_token_result or 'access_token' not in garena_token_result:
            return jsonify({"status": "error", "message": "Garena Authentication Failed"}), 401

        major_login_result = get_major_login(garena_token_result["access_token"], garena_token_result["open_id"])
        if not major_login_result or 'token' not in major_login_result:
            return jsonify({"status": "error", "message": "Major Login Failed"}), 401

        player_data = get_player_personal_show(
            major_login_result["serverUrl"], 
            major_login_result["token"], 
            int(uid), 
            bool(need_gallery_info), 
            int(call_sign_src),
            bool(need_blacklist), 
            bool(need_spark_info)
        )
        
        if not player_data:
            return jsonify({"status": "error", "message": f"No player data found for UID: {uid}"}), 404
        
        return jsonify(player_data), 200, {'Content-Type': 'application/json; charset=utf-8'}
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

# ==================== DISCORD PLAYER COMMAND ====================
@bot.tree.command(name="player", description="Check Free Fire Full Profile Stats via Custom Backend")
@app_commands.describe(uid="Player UID", server="Server Region (e.g., BD, IND)")
async def player_slash(interaction: discord.Interaction, uid: str, server: str = "BD"):
    await interaction.response.send_message(f"🔍 Fetching full profile details for UID: `{uid}` ...", ephemeral=True)
    
    server = server.upper()
    if server not in accounts:
        server = "BD"

    try:
        garena_token_result = get_garena_token(accounts[server]['uid'], accounts[server]['password'])
        if not garena_token_result or 'access_token' not in garena_token_result:
            await interaction.edit_original_response(content="❌ Garena Authentication Failed inside Bot!")
            return

        major_login_result = get_major_login(garena_token_result["access_token"], garena_token_result["open_id"])
        if not major_login_result or 'token' not in major_login_result:
            await interaction.edit_original_response(content="❌ Major Login Failed inside Bot!")
            return

        player_data = get_player_personal_show(
            major_login_result["serverUrl"], 
            major_login_result["token"], 
            int(uid), 
            False, 7, False, False
        )

        if not player_data:
            embed = discord.Embed(title="❌ Profile Not Found", color=0xFF0000)
            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="Status", value="Could not retrieve profile stats for this UID from game server.", inline=False)
            await interaction.edit_original_response(content=None, embed=embed)
            return

        account_info = player_data.get("accountInfo", player_data.get("basic_info", player_data))
        
        p_name = account_info.get("accountName", account_info.get("name", "Unknown"))
        p_level = account_info.get("accountLevel", account_info.get("level", "N/A"))
        p_likes = account_info.get("favorable", account_info.get("likes", "N/A"))
        p_guild = account_info.get("guildInfo", {}).get("guildName", account_info.get("guild_name", "None"))
        p_region = server

        embed = discord.Embed(title="🎮 Free Fire Full Profile Stats", color=0x00FFCC)
        embed.add_field(name="👤 Player Name", value=str(p_name), inline=True)
        embed.add_field(name="🆔 UID", value=str(uid), inline=True)
        embed.add_field(name="⭐ Level", value=str(p_level), inline=True)
        embed.add_field(name="🌍 Region", value=str(p_region), inline=True)
        embed.add_field(name="❤️ Likes", value=str(p_likes), inline=True)
        embed.add_field(name="🛡️ Guild Name", value=str(p_guild), inline=True)
        embed.set_footer(text="AuraFFX Custom Protobuf Bot • Powered by Flask Backend")
        
        await interaction.edit_original_response(content=None, embed=embed)

    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Error fetching player info: `{e}`")

# ==================== Run Flask & Bot Concurrently ====================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN.strip())
    else:
        print("❌ এরর: DISCORD_TOKEN এনভায়রনমেন্ট ভ্যারিয়েবল সেট করা নেই!")
