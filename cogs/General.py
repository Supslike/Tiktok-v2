# MAIN IMPORTS
import os
import pytz
import discord
import datetime
from replit import db
from discord.ext import commands
from utility import Naoki_v2 as naoki

# CONSTANT VARIABLES
Naoki = naoki.NaokiV2()
MAP = {False: "**OFF**", True: "**ON**"}
SETTING_OPTIONS = {1: "Show Analytics", 2: "Delete Message", 3: "Show Message", 4: "Reply with Error", 5: "Auto Download", 6: "Spoiler Videos"}

# General cog: For casual commands
class general(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # Checks if bot is responsive. If not, restarts the whole thing
  @commands.command()
  async def ping(self, ctx):
    try:
      await ctx.reply(f"{ctx.author.display_name}, I am ready to download! ")
    except discord.HTTPException:
      os.system("kill 1")

  # Sends Command List
  @commands.command()
  async def help(self, ctx):
    embed = discord.Embed(title="Command List", description="PREFIX: ``t!``")
    embed.add_field(name="Command: help", value=">  Shows this message", inline=False)
    embed.add_field(name="Command: ping", value=">  Checks if the bot is responding", inline=False)
    embed.add_field(name="Command: ping", value=">  Checks if the bot is responding", inline=False)
    embed.add_field(name="Command: download <link>", value=">  Downloads DailyMotion, Facebook, and Instagram videos", inline=False)
    embed.add_field(name="Command: tiktok <link>", value=">  Download specifically for tiktok videos only | slideshows are not supported", inline=False)
    embed.add_field(name="Command: set <setting>", value=">  Activate/Deactivate an option", inline=False)
    embed.add_field(name="Command: settings", value=">  Shows your settings", inline=False)
    embed.add_field(name="Command: source <optional: message_id>", value=">  Dms you the source of what you replied", inline=False)
    embed.add_field(name="Command: adv_help", value=">  Sends the owner-only commands", inline=False)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
    embed.set_thumbnail(url=ctx.guild.icon)
    gmt = pytz.timezone('Asia/Macau')
    gmt = datetime.datetime.now(gmt)
    philtime = gmt.strftime("%a, %d %b %Y %I:%M:%S %p GMT+8")
    embed.set_footer(text=f"{philtime}")
    await ctx.send(embed=embed)

  # Returns user settings
  @commands.command(aliases=["sett", "setting"])
  async def settings(self, ctx, user: discord.Member = None):
    if user == None:
      user = ctx.author
    user_data = Naoki.get_user(user.id)
    final = ""
    for option in user_data:
      final += f"- __{option}__: {MAP[user_data[option]]}\n"
    await ctx.reply(f"## **[+] __{user.display_name}'s Data__**\n\n{final}")
  
  # Activates / deactivates a setting
  @commands.command()
  async def set(self, ctx, *, setting: int = None):
    user_data = Naoki.get_user(ctx.author.id)
    settings = ""
    number = 0
    for set in user_data:
      number += 1
      settings += f"{number}.   {set} \n"
    try:
      current_set = user_data[SETTING_OPTIONS[setting]] 
    except KeyError:
      await ctx.reply(f"**__{setting}__** is not found. Please input the *__number__* of the setting you want to modify. The following available settings are: \n\n{settings}\n\n\n")
      return
    if current_set:
      user_data[SETTING_OPTIONS[setting]] = False
      await ctx.reply(f"**__{SETTING_OPTIONS[setting]}__** is now **__OFF__**")
    else:
      user_data[SETTING_OPTIONS[setting]] = True
      await ctx.reply(f"**__{SETTING_OPTIONS[setting]}__** is now **__ON__**")
    Naoki.dump_data(ctx.author.id, user_data)

  # Sends a source data of a video naoki has already sent
  @commands.command()
  async def source(self, ctx, message_id: int = None):
    await ctx.message.delete()
    data = db["source"]
    if ctx.message.reference and message_id == None:
      if str(ctx.message.reference.message_id) in data:
        link_data = data[str(ctx.message.reference.message_id)]
        await ctx.author.send(f"# Source: \n\n - Tiktok link:  <{link_data['url']}>\n - From:  {link_data['author']}\n- Channel:  {link_data['channel']}\n- Message:  <#{link_data['message_url']}>\n- Download Link:  <||{link_data['video_url']}||>")
      else:
        await ctx.author.send(f"# Source: \n\n ``{ctx.message.reference.message_id}``  NOT FOUND!")
    if not ctx.message.reference and message_id != None:
      if str(message_id) in data:
        link_data = data[str(message_id)]
        await ctx.author.send(f"# Source: \n\n - Tiktok link:  <{link_data['url']}>\n - From:  {link_data['author']}\n- Channel:  {link_data['channel']}\n- Message:  <#{link_data['message_url']}>\n- Download Link:  <||{link_data['video_url']}||>")
      else:
        await ctx.author.send(f"# Source: \n\n ``{message_id}``  NOT FOUND!")
    if not ctx.message.reference and message_id == None:
      await ctx.author.send("# Source: \n\n ``NONE``  NOT FOUND!\n\n Please input a message ID of the vid or reply to the video.")

  # Sends a help for owner-only commands
  @commands.command()
  async def adv_help(self, ctx):
    embed = discord.Embed(title=":warning: Owner-Only Command List", description="PREFIX: ``t!``")
    embed.add_field(name="Command: source_clean", value=">  Clears the saved sources on the database", inline=False)
    embed.add_field(name="Command: saved_clean", value=">  Clears the saved videos on the database", inline=False)
    embed.add_field(name="Command: queue_clean", value=">  Clears the queue if ever somethinng gets stucked", inline=False)
    embed.add_field(name="Command: source_check", value=">  Sends the saved sources on the database", inline=False)
    embed.add_field(name="Command: saved_check", value=">  Sends the saved videos on the database", inline=False)
    embed.add_field(name="Command: load <cog_name>", value=">  Loads Cog", inline=False)
    embed.add_field(name="Command: unload <cog_name>", value=">  Unloads Cog", inline=False)
    embed.add_field(name="Command: reload <cog_name>", value=">  Reloads cog", inline=False)
    embed.add_field(name="Command: cc", value=">  Sends Cog Status", inline=False)
    embed.add_field(name="Command: report", value=">  Sends API status", inline=False)
    embed.add_field(name="Command: restart", value=">  Restarts the bot", inline=False)
    embed.add_field(name="Command: switch", value=">  Switches API usage", inline=False)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
    embed.set_thumbnail(url=ctx.guild.icon)
    gmt = pytz.timezone('Asia/Macau')
    gmt = datetime.datetime.now(gmt)
    philtime = gmt.strftime("%a, %d %b %Y %I:%M:%S %p GMT+8")
    embed.set_footer(text=f"{philtime}")
    await ctx.send(embed=embed)

# COG SETUP
async def setup(bot):
  await bot.add_cog(general(bot))
