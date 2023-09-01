# MAIN IMPORTS
import os
import time
import json
import asyncio
import discord
import traceback
from replit import db
from utility import System_Functions

# A message variable builder, so datas are easily navigateable
class Builder():
  def __init__(self, msg, emoji, bot, url, ctx = False):
    async def reply(content="", file = None, refer = msg, embed=None):
      return await msg.channel.send(content, file = file, reference = refer, embed=embed)
    self.author = msg.author
    self.emoji = emoji
    self.bot = bot
    self.url = url
    self.guild = msg.guild
    self.id = msg.id
    self.channel = msg.channel
    if ctx:
      self.msg = msg.message
      self.send = msg.send
      self.reply = msg.reply
      self.delete = msg.message.delete
      self.content = msg.message.content
    else:
      self.msg = msg
      self.send = msg.channel.send
      self.delete = msg.delete
      self.reply = reply
      self.content = msg.content
    self.content = str(self.content).replace(self.url, "")

# Naoki v2: Former "Tiktok Bot"
class NaokiV2():
  def __init__(self):
    self._QUEUE = []

  # Removes all items in queue if ever something gets stucked
  def Clean(self):
    self._QUEUE = []

  # Dumps data both in database and JSON
  def dump_data(self, user_id, new_data):
    with open("./tt/user_options.json", "r") as f:
      data = json.load(f)
    data[str(user_id)] = new_data
    with open("./tt/user_options.json", "w") as f:
      json.dump(data, f, indent=4)
    db["user_options"][user_id] = new_data

  # Retrieves user data 
  def get_user(self, user_id):
      with open("./tt/user_options.json", "r") as f:
        data = json.load(f)
      if str(user_id) in data:
        return data[str(user_id)]
      else:
        new_data = {"Show Analytics": False, "Delete Message": False, "Show Message": True, "Reply with Error": False, "Auto Download": False, "Spoiler Videos": False}
        data[str(user_id)] = new_data
        with open("./tt/user_options.json", "w") as f:
          json.dump(data, f, indent=4)
        db["user_options"][user_id] = new_data
        return data[str(user_id)]

  # Goes through user options and processes each one
  async def _process_user_options(self, user_options, msg, current_time):
    content = ""
    reply = True
    filename = "./tt/video.mp4"
    if user_options["Delete Message"]:
      reply = False
      await msg.delete()
    if user_options["Show Message"]:
      if msg.content != "":
        content += f"``{msg.author.display_name}``:  " + msg.content + "\n\n"
    if user_options["Show Analytics"]:
      content += f"||Took: {current_time}s\nLink by: {msg.author.display_name}\nOriginal link: <{msg.url}>\n||"
    if "|" in msg.content:
      if user_options["Spoiler Videos"]:
        filename = "./tt/SPOILER_video.mp4"
        os.rename("./tt/video.mp4", filename)
    return content, reply, filename

  # Catching errors
  async def process_error(self, user_options, msg, error_msg=""):
    try:
      self._QUEUE.pop(0)
    except IndexError:
      pass
    reply = True
    embed = discord.Embed(color=discord.Color.from_rgb(255, 0, 0), description=f":no_entry: **{error_msg}**")
    try:
      os.remove("./tt/video.mp4")
    except:
      pass
    if user_options["Delete Message"]:
      reply = False
      try:
        await msg.delete()
      except:
        pass
    elif not user_options["Delete Message"]:
      try:
        await self._remove_emoji(msg.msg, msg.emoji, msg.bot.user)
        if "System" in error_msg:
          await self._add_emoji(msg.msg, "⚠")
        else:
          await self._add_emoji(msg.msg, "❌")
      except:
        pass
    if error_msg == "":
      return
    if user_options["Reply with Error"]:
      if reply:
        try:
          await msg.reply(embed=embed)
        except:
          pass
      elif not reply:
        await msg.send(embed = embed)

  # Handles the whole download process
  async def process_download(self, msg, url, type_usage, emoji, bot, ctx = False):
    message = Builder(msg, emoji, bot, url, ctx)
    user_options = self.get_user(message.author.id)
    reply_queue = False
    if len(self._QUEUE) > 0:
      self._QUEUE.append(message.id)
      if not await self._add_emoji(message.msg, emoji):
        await self.process_error(user_options, message)
        return
      try:
        embed = discord.Embed(color=discord.Color.from_rgb(255, 0, 0), description=f":no_entry: **Downloading Video.... Line in QUEUE: {len(self._QUEUE)}**")
        queuemsg = await message.reply(embed=embed)
        reply_queue = True
      except Exception as e:
        reply_queue = False
        await self.process_error(user_options, message, e)
        return
      while self._QUEUE[0] != message.id:
        await asyncio.sleep(1)
    else:
      self._QUEUE.append(message.id)
    if not await self._add_emoji(message.msg, emoji):
      await self.process_error(user_options, message)
      return
    if reply_queue:
      await queuemsg.delete()
    start_time = time.perf_counter() 
    try:
      video = System_Functions.get_video(message.url, type_usage)
      res, url = await video.download()
    except EnvironmentError:
      traceback.print_last()
      await self.process_error(user_options, message, "System Bugs have occured please try again later...")
      return
    except Exception as e:
      traceback.print_last()
      await self.process_error(user_options, message, e)
      return
    current_time = str(round(time.perf_counter() - start_time, 2))
    self._print_console(message, "download")
    if res == False and url == False:
      await self.process_error(user_options, message, "System service unavailable... Please try again soon!")
      return
    if res == None:
      await self.process_error(user_options, message, "Invalid URL!")
      return
    if not await self._remove_emoji(message.msg, emoji, bot.user):
      await self.process_error(user_options, message)
      return
    content, reply, filename = await self._process_user_options(user_options, message, current_time)
    if reply:
      if res:
        file = discord.File(filename)
        msg = await message.reply(content=f"{content}", file=file)
      elif not res:
        msg = await message.reply(content=f"{content} \n{url}")
    elif not reply:
      if res:
        file = discord.File(filename)
        msg = await message.send(content=f"{content}", file=file)
      elif not res:
        msg = await message.send(content=f"{content} \n{url}")
    self._QUEUE.pop(0)
    try:
      os.remove(filename)
    except:
      pass

    # Logs video data
    db["source"][str(msg.id)] = {"url": message.url, "video_url": msg.attachments[0].url, "author": str(message.author.display_name), "channel": str(message.channel), "message_url": str(msg.jump_url)}
    db["saved"][str(message.url)] = msg.attachments[0].url

  # Add emoji
  async def _add_emoji(self, msg, emoji):
    try:
      await msg.add_reaction(emoji)
      return True
    except:
      return False

  # Remove Emoji
  async def _remove_emoji(self, msg, emoji, user):
    try:
      await msg.remove_reaction(emoji, user)
      return True
    except:
      return False

  # Download Report for API monitoring
  def _print_console(self, msg, usage_type: str):
    if "download":
      try:
        print(f"\n\n[+] DOWNLOAD REPORT: \n\n- Link: {msg.url}\n- Author: {msg.author.display_name}\n- Server: {msg.guild.name}\n- Channel: {msg.msg.channel.name}\n - Message link: {msg.msg.jump_url}\n\n")
      except:
        print("[+] ERROR DETECTED")

  # Call this function if ever its your first time booting it in https://replit.com
  def first_boot(self):
    db["source"] = {}
    db["saved"] = {}
    db["user_optios"] = {}
