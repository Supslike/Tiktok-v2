# MAIN IMPORTS
import os
import re
import discord
from discord.ext import tasks
from discord.ext import commands
from utility import Naoki_v2 as naoki
from utility import keep_alive as idle

# Discord client
bot = commands.Bot(command_prefix = "t!",intents = discord.Intents.all(), help_command = None, status = discord.Status.idle)


# CONSTANT VARIABLES
Naoki = naoki.NaokiV2()
SPECIAL = False
MAP = {False: "**OFF**", True: "**ON**"} # Dictionary for string ON and OFF string
COGS = ["Database", "General", "Monitor"]


# BOT EVENTS

# At startup
@bot.event
async def on_ready():
  # Downloads bot's avatar for flasks webserver profile
  await bot.user.avatar.save("./static/bot_profile.jpg") 
  
  # Loading up cogs
  print("\n\n\n[+] START UP STARTED")
  global COGS
  cogs = []
  for filename in os.listdir("./cogs"):
    try:
      if filename.endswith(".py"):
        await bot.load_extension(f"cogs.{filename[:-3]}")
        print(f"[+] Loaded cog {filename}!")
        cogs = [filename[:-3]]
    except Exception as e:
      print(f"[-] SOMETHING WENT WRONG WITH TRYING TO LOAD {filename}\n\n{e}\n\n")
  COGS = cogs
  print(f"[+] READY TO DOWNLOAD: {bot.user}")
  live_presence.start() # Start loop event

 # if error occured on commands
@bot.event
async def on_command_error(ctx, error):
  # Void return IF statements to avoid common user input errors
  if "not found" in str(error):
    return
  if "required argument that is missing." in str(error):
    return
  print(f'SOMETHING WENT WRONG: {error}')
  print(f"LOCATED: {ctx.channel}, {ctx.author.display_name}, {ctx.message.content}")
  await Naoki.process_error(Naoki.get_user(ctx.author.id), naoki.Builder(ctx, "", bot, "", True), error)


# COG COMMANDS

# Loads a cog
async def load_cog(name):
  try:
    await bot.load_extension(f"cogs.{name}")
    return True, "Success!"
  except commands.ExtensionAlreadyLoaded:
    return False, "Already loaded!"
  except commands.ExtensionNotFound:
    return False, f"Cog {name} is not found!"
  except Exception as e:
    return False, e

# Unloads a cog
async def unload_cog(name):
  try:
    await bot.unload_extension(f"cogs.{name}")
    return True, "Success!"
  except commands.ExtensionNotLoaded:
    return False, "Already unloaded!"
  except commands.ExtensionNotFound:
    return False, f"Cog {name} is not found!"
  except Exception as e:
    return False, e

# Loads a specific cog
@bot.command(aliases=["load"])
async def loads(ctx, cog_name):
  info = await bot.application_info() 
  if ctx.author.id == info.owner.id: # Checks if user is the bot's owner
    if cog_name == "all":
      cogs = COGS
    else:
      cogs = [cog_name]
      
    report = "# REPORT: \n\n"
    for cog in cogs:
      res, mes = await load_cog(cog)
      if res:
        report += f"[+] Success loading **``{cog}``**!\n"
      elif not res:
        report += f"[-] Something went wrong in trying to **load** **``{cog}``**!\n[-] **``{cog}``**: {mes}\n"
    await ctx.send(report)

# Unloads a specific cog
@bot.command(aliases=["unload"])
async def unloads(ctx, cog_name):
  info = await bot.application_info() # Checks if user is the bot's owner
  if ctx.author.id == info.owner.id:
    if cog_name == "all":
      cogs = COGS
    else:
      cogs = [cog_name]
      
    report = "# REPORT: \n\n"
    for cog in cogs:
      res, mes = await unload_cog(cog)
      if res:
        report += f"[+] Success unloading **``{cog}``**!\n"
      elif not res:
        report += f"[-] Something went wrong in trying to **unload** **``{cog}``**!\n[-] **``{cog}``**: {mes}\n"
    await ctx.send(report)

# Reloads a cog
@bot.command(aliases=["reload"])
async def reloads(ctx, cog_name):
  info = await bot.application_info() # Checks if user is the bot's owner
  if ctx.author.id == info.owner.id:
    if cog_name == "all":
      cogs = COGS
    else:
      cogs = [cog_name]
      
    report = "# REPORT: \n\n"
    for cog in cogs:
      res, mes = await unload_cog(cog)
      if res:
        report += f"[+] Success unloading **``{cog}``**!\n"
      elif not res and mes == "Already unloaded!":
        report += f"[+] **``{cog}``** is already unloaded!\n"
      elif not res:
        report += f"[-] Something went wrong in trying to **unload** **``{cog}``**!\n[-] **``{cog}``**: {mes}\n"
      res, mes = await load_cog(cog)
      if res:
        report += f"[+] Success loading **``{cog}``**!\n"
      elif not res:
        report += f"[-] Something went wrong in trying to **load** **``{cog}``**!\n[-] **``{cog}``**: {mes}\n"
    await ctx.send(report)

# Checks the cog's status
@bot.command(aliases=["checkcog","cc"])
async def cogscheck(ctx, cog_provided = None):
  info = await bot.application_info() # Checks if user is the bot's owner
  if ctx.author.id == info.owner.id:
    report = "# REPORT: \n\n"
    if cog_provided == None:
      cogs = COGS
    else:
      cogs = [cog_provided]
    for cog_name in cogs:
      try:
        await bot.load_extension(f"cogs.{cog_name}")
        report += f"**{cog_name}**:  Unloaded!\n"
        await bot.unload_extension(f"cogs.{cog_name}")
      except commands.ExtensionAlreadyLoaded:
        report += f"**{cog_name}**:  Loaded!\n"
      except commands.ExtensionNotFound:
        report += f"**{cog_name}**:  Not found!\n"      
    await ctx.send(report)


# NAOKI MAIN COMMANDS


# Switches API if ever the other one rans out of calls
@bot.command()
async def switch(ctx):
  info = await bot.application_info() # Checks if user is the bot's owner
  if ctx.author.id == info.owner.id:
    global SPECIAL
    if SPECIAL:
      SPECIAL = False
    else:
      SPECIAL = True
    await ctx.send(f"SWITCHED API, Priority is now {MAP[SPECIAL]}")

# Cleans the queue if ever something is stucked in a queue
@bot.command()
async def queue_clean(ctx):
  info = await bot.application_info() # Checks if user is the bot's owner
  if ctx.author.id == info.owner.id:
    Naoki.Clean()
    await ctx.send("SUCCESS CLEANING!")

# Main command for specifically downloading tiktoks
@bot.command()
async def tiktok(ctx, main_url):
  emoji = bot.get_emoji(1144941184310067240)
  if SPECIAL:
    await Naoki.process_download(ctx, main_url, "priority", emoji, bot, True)
  else:
    await Naoki.process_download(ctx, main_url, "tiktok", emoji, bot, True)

# Command for downloading videos from different platforms
@bot.command()
async def download(ctx, main_url):
  emoji = bot.get_emoji(1144941184310067240)
  await Naoki.process_download(ctx, main_url, "multi", emoji, bot, True)


# MESSAGE EVENT FOR AUTO DOWNLOAD


# Message Event
@bot.event
async def on_message(msg):
  # Checks if user is a bot
  if msg.author.bot:
    return
  
  # Checks if the message is a command
  if msg.content.startswith("t!"):
    await bot.process_commands(msg)
    return

  # Retrieves all the links found in user's message
  try:
    main_url = re.search("(?P<url>https?://[^\s]+)", str(msg.content)).group("url")
  except AttributeError:
    await bot.process_commands(msg)
    return

  # Checks if auto download is ON
  user_options = Naoki.get_user(msg.author.id)
  if not user_options["Auto Download"]:
    return
  emoji = bot.get_emoji(1144941184310067240)
  
  # If tiktok.com is found in the URL
  if "tiktok.com" in main_url:
    if SPECIAL:
      await Naoki.process_download(msg, main_url, "priority", emoji, bot, False)
    else:
      await Naoki.process_download(msg, main_url, "tiktok", emoji, bot, False)

  # If one of these links is found in the URL
  if "instagram.com/reel" in main_url or "facebook.com/watch" in main_url or "dailymotion.com/video/" in main_url or "https://fb.watch" in main_url:
    await Naoki.process_download(msg, main_url, "multi", emoji, bot, False)
    

# A live presence change
@tasks.loop(seconds=60) 
async def live_presence():
  xMAP = {True: "ON", False: "OFF"}
  activity = discord.Activity(type=discord.ActivityType.watching, name=f'Tiktok! | Priority is {xMAP[SPECIAL]}')
  await bot.change_presence(status=discord.Status.idle, activity=activity)

# For replit 24/7 hosting
idle.keep_alive()

# Runs the bot
try:
  bot.run(os.getenv("tuken"), log_handler=None)
except discord.HTTPException:
  os.system("kill 1")