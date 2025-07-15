import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import webserver

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready(): #runs when bot is online
    await bot.tree.sync()
    print(f"{bot.user} online")

class OutreachSessionDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="No sessions yet, check in later!", value="session1"),

        ]
        super().__init__(placeholder="Select an outreach session", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Check back when volunteer sessions start!", ephemeral=True)
class OutreachSessionView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(OutreachSessionDropdown())

""" @bot.event
async def on_message(msg):
    if msg.author.id != bot.user.id:  # Ignore messages from the bot 
        await msg.channel.send(f"nice, {msg.author.mention}") """

@bot.tree.command(name="practice-hours", description = "Check practice hours")
@app_commands.describe(student_id="Your student ID")
async def hours(interaction: discord.Interaction, student_id: int):
    url = f"https://hrs-db-api-wwrobo.ftcscoring.app/aggregate/member/practice/{student_id}"
    try:
        response = requests.get(url, timeout=5)
        try:
            data = response.json()
        except Exception:
            await interaction.response.send_message("Error: Could not parse API response. Please try again later.", ephemeral=True)
            return 
        if response.status_code == 200 and "minutes" in data:
            hours_val = data["minutes"] // 60 
            minutes_val = data["minutes"] % 60
            embed = discord.Embed(
                title="Practice Hours",
                color=discord.Color.dark_orange()
            )
            embed.add_field(name="Student ID", value=str(student_id), inline=True)
            embed.add_field(name="practice Hours", value= f"{hours_val} hours and {minutes_val} minutes", inline=False)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            embed4 = discord.Embed(
                title="No valid practice hour data found",
                description=f"Student {student_id} has 0 practice hours.",
                color=discord.Color.dark_orange()
            )
            await interaction.response.send_message(embed=embed4, ephemeral=True)

    except Exception as e: 
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Error fetching data: {e}", ephemeral=True)


 
#OUTREACH HOURS


@bot.tree.command(name="outreach-hours", description = "Check Outreach hours")
@app_commands.describe(student_id="Your student ID")
async def hours2(interaction2: discord.Interaction, student_id: int):
    url = f"https://hrs-db-api-wwrobo.ftcscoring.app/aggregate/member/outreach/{student_id}"
    try:
        response = requests.get(url, timeout=5)
        try:
            data = response.json()
        except Exception:
            await interaction2.response.send_message("Error: Could not parse API response. Please try again later.", ephemeral=True)
            return 
        if response.status_code == 200 and "minutes" in data:
            hours_val = data["minutes"] // 60 
            minutes_val = data["minutes"] % 60
            embed = discord.Embed(
                title="Outreach Hours",
                color=discord.Color.dark_green()
            )
            embed.add_field(name="Student ID", value=str(student_id), inline=True)
            embed.add_field(name="Outreach Hours", value= f"{hours_val} hours and {minutes_val} minutes", inline=False)
            embed.set_thumbnail(url=interaction2.user.display_avatar.url)
            await interaction2.response.send_message(embed=embed, view=OutreachSessionView(), ephemeral=True)

        else:
            embed4 = discord.Embed(
                title="No valid outreach hour data found",
                description=f"Student {student_id} has 0 outreach hours.",
                color=discord.Color.dark_green()
            )
            await interaction2.response.send_message(embed=embed4, ephemeral=True)

    except Exception as e: 
        if not interaction2.response.is_done():
            await interaction2.response.send_message(f"Error fetching data: {e}", ephemeral=True)


webserver.keep_alive()
bot.run(os.getenv("DISCORD_TOKEN")) #runs the bot with the token from the .env file