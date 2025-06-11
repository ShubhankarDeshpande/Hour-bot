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
async def hours(interaction: discord.Interaction, student_id: int, ctx):
    url = "http://hours.westwoodrobots.org/hours"
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
                    title="Student Practice Hours",
                    color=discord.Color.dark_orange()
                )
                embed.add_field(name="Student ID", value=str(id_num), inline=True)
                embed.add_field(name="Practice Hours", value=hours, inline=False)
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                idfound = True
                break
        if not idfound:
            embed2 = discord.Embed(
                title="Student Not Found",
                description=f"Student ID {student_id} not found.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed2, ephemeral=True)

    except Exception as e: 
        await interaction.response.send_message(f"Error fetching data: {e}")



#OUTREACH HOURS


@bot.tree.command(name="outreach-hours", description = "Check Outreach hours")
@app_commands.describe(student_id="Your student ID")
async def hours(interaction: discord.Interaction, student_id: int):
    url = "http://hours.westwoodrobots.org/volunteer-hours"
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')

        trs = soup.find_all("tr")
        idfound = False
        for tr in trs:
            tds = tr.find_all("td")#gets all the table td's
            if len(tds) < 4:
                continue #skips rows with less than 4 tds
            if(len(tds) % 4 == 0):
                atag = tds[0].find("a", class_="student-link")
                id_text = atag.get_text(strip=True)

            try: 
                id_num = int(id_text) #gets only the digits from the id_text
            except ValueError:
                continue
            if id_num == student_id:
                hours = tds[1].get_text(strip=True)
                embed = discord.Embed(
                    title="Outreach Hours",
                    color=discord.Color.dark_green()
                )
                embed.add_field(name="Student ID", value=str(id_num), inline=True)
                embed.add_field(name="Hours", value=hours, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                idfound = True
                break
        
        if not idfound:
            embed2 = discord.Embed(
                title="Student Not Found",
                description=f"Student ID {student_id} not found.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed2, ephemeral=True)

    except Exception as e: 
        await interaction.response.send_message(f"Error fetching data: {e}")


webserver.keep_alive()
bot.run(os.getenv("DISCORD_TOKEN")) #runs the bot with the token from the .env file