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









#PRACTICE HOURS
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
            embed.add_field(name="Practice Hours", value= f"{hours_val} hours and {minutes_val} minutes", inline=False)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            errorembed = discord.Embed(
                title="No valid practice hour data found",
                description=f"Student {student_id} has 0 practice hours.",
                color=discord.Color.dark_orange()
            )
            await interaction.response.send_message(embed=errorembed, ephemeral=True)

    except Exception as e: 
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Error fetching data: {e}", ephemeral=True)


 
#OUTREACH HOURS SECTION


#ROBOCAMP DAY DROPDOWN
class RobocampDayDropdown(discord.ui.Select):
    def __init__(self,student_id, weeknumber):
        self.student_id = student_id
        self.weeknumber = weeknumber
        options = [
            discord.SelectOption(label="Robocamp week " + self.weeknumber + " day 1", value = "1"),
            discord.SelectOption(label="Robocamp week " + self.weeknumber + " day 2", value = "2"),
            discord.SelectOption(label="Robocamp week " + self.weeknumber + " day 3", value = "3"),
            discord.SelectOption(label="Robocamp week " + self.weeknumber + " day 4", value = "4"),
            discord.SelectOption(label="Robocamp week " + self.weeknumber + " day 5", value = "5"),
        ]
        super().__init__(placeholder="Select a Robocamp day", options=options)

    async def callback(self, interaction4: discord.Interaction):
        selected = self.values[0]
        if selected in ["1", "2", "3", "4", "5"]:
            totaldaymins = 0
            Sessionembed = discord.Embed(
                title="Robocamp Week " + self.weeknumber + " Day " + selected + " Hours",
                color=discord.Color.dark_green()
            )
            url = f"https://hrs-db-api-wwrobo.ftcscoring.app/outreach/Robocamp%20W{self.weeknumber}D{selected}/aggregate/{self.student_id}"
            print(self.weeknumber + " " + selected + " " + str(self.student_id))
            try:
                response = requests.get(url, timeout=5)
                try:
                    data = response.json()
                except Exception:
                    await interaction4.response.send_message("Error: Could not parse API response. Please try again later.", ephemeral=True)
                    return

                if "minutes" in data and response.status_code == 200:
                    totaldaymins = data["minutes"]
                    print(f"totalminutes: {totaldaymins}")
            except Exception as e:
                print(f"Error fetching data for Robocamp Week {self.weeknumber} Day {selected}: {e}")

            Sessionembed.add_field(name="Student ID", value=str(self.student_id), inline=True)
            Sessionembed.add_field(name="Robocamp Week " + str(self.weeknumber) + " Day " + selected + " Hours", value= f"{totaldaymins//60} hours and {totaldaymins%60} minutes", inline=False)
            Sessionembed.set_thumbnail(url=interaction4.user.display_avatar.url)
            print(totaldaymins)
            await interaction4.response.send_message(embed=Sessionembed, view = RobocampDayView(self.student_id, self.weeknumber), ephemeral=True)

class RobocampDayView(discord.ui.View):
    def __init__(self, student_id, week_number):
        super().__init__()
        self.add_item(RobocampDayDropdown(student_id, week_number))






#ROBOCAMP WEEK DROPDOWN AND OUTREACH SESSION DROPDOWN
class OutreachSessionDropdown(discord.ui.Select):
    def __init__(self,student_id):
        self.student_id = student_id
        options = [
            discord.SelectOption(label="Robocamp week 1", value = "1"),
            discord.SelectOption(label="Robocamp week 2", value = "2"),
            discord.SelectOption(label="Robocamp week 3", value = "3"),
        ]
        super().__init__(placeholder="Select an outreach session", options=options)

    async def callback(self, interaction3: discord.Interaction):
        selected = self.values[0]
        week_str = f"{selected}"
        if selected in ["1", "2", "3"]:
            totalminutes = 0
            i = 0
            Sessionembed = discord.Embed(
                title="Robocamp Week " + str(selected),
                color=discord.Color.dark_green()
            )

            for i in range(1, 6):
                url = f"https://hrs-db-api-wwrobo.ftcscoring.app/outreach/Robocamp%20W{week_str}D{i}/aggregate/{self.student_id}"
                try:
                    response = requests.get(url, timeout=5)
                    try:
                        data = response.json()
                    except Exception:
                        await interaction3.response.send_message("Error: Could not parse API response. Please try again later.", ephemeral=True)
                        return 
                    
                    if "minutes" in data and response.status_code == 200:
                        totalminutes += data["minutes"]
                        print(f"totalminutes: {totalminutes}")
                except Exception as e:
                    print(f"Error fetching data for Robocamp Week {week_str} Day {i}: {e}")
            
            Sessionembed.add_field(name="Student ID", value=str(self.student_id), inline=True)
            Sessionembed.add_field(name="Robocamp Week " + str(week_str) + " Hours", value= f"{totalminutes//60} hours and {totalminutes%60} minutes", inline=False)
            Sessionembed.set_thumbnail(url=interaction3.user.display_avatar.url)
            print(totalminutes)
            await interaction3.response.send_message(embed=Sessionembed, view = RobocampDayView(self.student_id, week_str), ephemeral=True)

class OutreachSessionView(discord.ui.View):
    def __init__(self, student_id):
        super().__init__()
        self.add_item(OutreachSessionDropdown(student_id))









#TOTAL OUTREACH HOURS EMBED


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
            embed.add_field(name="Total outreach Hours", value= f"{hours_val} hours and {minutes_val} minutes", inline=False)
            embed.set_thumbnail(url=interaction2.user.display_avatar.url)
            await interaction2.response.send_message(embed=embed, view=OutreachSessionView(student_id), ephemeral=True)

        else:
            errorembed2 = discord.Embed(
                title="No valid outreach hour data found",
                description=f"Student {student_id} has 0 outreach hours.",
                color=discord.Color.dark_green()
            )
            errorembed2.set_thumbnail(url=interaction2.user.display_avatar.url)
            await interaction2.response.send_message(embed=errorembed2, ephemeral=True)

    except Exception as e: 
        if not interaction2.response.is_done():
            await interaction2.response.send_message(f"Error fetching data: {e}", ephemeral=True)


webserver.keep_alive()
bot.run(os.getenv("DISCORD_TOKEN")) #runs the bot with the token from the .env file