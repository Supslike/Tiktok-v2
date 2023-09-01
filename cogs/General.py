# MAIN IMPORTS
import os
import discord
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
    await ctx.send(embed=await Naoki.embed(ctx))

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

# COG SETUP
async def setup(bot):
  await bot.add_cog(general(bot))