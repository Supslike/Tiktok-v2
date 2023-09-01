# MAIN IMPORTS
import json
from replit import db
from discord.ext import commands

# Database cog:  Handles functions that requires database manipulation
class database(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    # Loads user option from database to a JSON file to easily visualize data
    data = db["user_options"].value
    final_data = {}
    for msg in data:
      final_data[msg] = data[msg].value
    with open("./tt/user_options.json", "w") as f:
      json.dump(final_data, f, indent=4)

  # Removes all saved videos data
  @commands.command()
  async def saved_clean(self, ctx):
    info = await self.bot.application_info() # Checks if user is the bot's owner
    if ctx.author.id == info.owner.id:
      try:
        await ctx.send(content=str(db["saved"].value))
      except:
        pass
      db["saved"] = {}
      await ctx.send("SUCCESS CLEANING!")

  # Sends all saved videos data
  @commands.command()
  async def saved_check(self, ctx):
    info = await self.bot.application_info() # Checks if user is the bot's owner
    if ctx.author.id == info.owner.id:
      await ctx.send(content=f'# SAVED VIDEOS:  ``{len(db["saved"])}``')
      try:
        await ctx.send(content=str(db["saved"].value))
      except:
        pass

  # Removes all source data of videos
  @commands.command()
  async def source_clean(self, ctx):
    info = await self.bot.application_info() # Checks if user is the bot's owner
    if ctx.author.id == info.owner.id:
      try:
        await ctx.send(content=str(db["source"].value))
      except:
        pass
      db["source"] = {}
      await ctx.send("SUCCESS CLEANING!")

  # Sends all source data of videos
  @commands.command()
  async def source_check(self, ctx):
    info = await self.bot.application_info() # Checks if user is the bot's owner
    if ctx.author.id == info.owner.id:
      await ctx.send(content=f'# SAVED SOURCES:  ``{len(db["source"])}``')
      try:
        await ctx.send(content=str(db["source"].value))
      except:
        pass
  

# COG SETUP
async def setup(bot):
  await bot.add_cog(database(bot))