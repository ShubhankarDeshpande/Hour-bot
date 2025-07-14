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


""" @bot.event
async def on_message(msg):
    if msg.author.id != bot.user.id:  # Ignore messages from the bot 
        await msg.channel.send(f"nice, {msg.author.mention}") """

@bot.tree.command(name="practice-hours", description = "Check practice hours")
@app_commands.describe(student_id="Your student ID")
async def hours(interaction: discord.Interaction, student_id: int):
    url = "https://hrs-db-api-wwrobo.ftcscoring.app/aggregate/member/practice/{student_id}"
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')

        trs = soup.find_all("tr")
        idfound = False
        for tr in trs:
            tds = tr.find_all("td")#gets all the table td's
            if len(tds) < 3:
                continue #skips rows with no
            if(len(tds) % 3 == 0):
                id_text = tds[0].get_text(strip=True)

            try: 
                id_num = int(''.join(filter(str.isdigit, id_text))) #gets only the digits from the id_text
            except ValueError:
                continue
            if id_num == student_id:
                hours = tds[1].get_text(strip=True)
                embed = discord.Embed(
                    title="Practice Hours",
                    color=discord.Color.dark_orange()
                )
                embed.add_field(name="Student ID", value=str(id_num), inline=True)
                embed.add_field(name="Practice Hours", value=hours, inline=False)
                embed.set_thumbnail(url=str(interaction.user.display_avatar.url))
                idfound = True
                await interaction.response.send_message(embed=embed, ephemeral=True)

                return
        if not idfound:
            embed4 = discord.Embed(
                title="Student Not Found",
                description=f"Student ID {student_id} not found.",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed4, ephemeral=True)

    except Exception as e: 
        if not interaction.response.is_done():
            await interaction.response.edit_message(f"Error fetching data: {e}")



#OUTREACH HOURS


@bot.tree.command(name="outreach-hours", description = "Check Outreach hours")
@app_commands.describe(student_id="Your student ID")
async def hours2(interaction2: discord.Interaction, student_id: int):
    url = "https://hrs-db-api-wwrobo.ftcscoring.app/aggregate/member/outreach/{student_id}"
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        if response.status_code == 200 and "minutes" in data:
            hours_val = round(data["minutes"] / 60, 2)  
            embed = discord.Embed(
                title="Outreach Hours",
                color=discord.Color.dark_orange()
            )
            embed.add_field(name="Student ID", value=str(student_id), inline=True)
            embed.add_field(name="Outreach Hours", value=f"{hours_val} hours", inline=False)
            embed.set_thumbnail(url=str(interaction2.user.display_avatar.url))
            await interaction2.response.send_message(embed=embed, ephemeral=True)

        else:
            embed4 = discord.Embed(
                title="Student Not Found",
                description=f"Student ID {student_id} not found.",
                color=discord.Color.red()
            )
            await interaction2.response.send_message(embed=embed4, ephemeral=True)

    except Exception as e: 
        if not interaction2.response.is_done():
            await interaction2.response.edit_message(f"Error fetching data: {e}", ephemeral=True)


webserver.keep_alive()
bot.run(os.getenv("DISCORD_TOKEN")) #runs the bot with the token from the .env file