# MAIN IMPORTS
import os
import sys
from replit import db
from discord.ext import commands

# Monitor cog: Commands for monitoring the bot
class monitor(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # Sends API status/data
  @commands.command()
  async def report(self, ctx):
    bot_info = await self.bot.application_info() # Checks if user is the bot's owner
    if ctx.author.id == bot_info.owner.id:
      data = db["ratelimits"]
      await ctx.send(f'\n\n\n**[+] API REPORT:**\n\n**TIKTOK**\n- Remaining: {data["tiktok"]["remaining"]}\n- Limit: {data["tiktok"]["limit"]}\n- Reset Time: {data["tiktok"]["reset"]}\n- Time Recorded: {data["tiktok"]["time_recorded"]}\n\n**PRIORITY**\n- Remaining: {data["priority"]["remaining"]}\n- Limit: {data["priority"]["limit"]}\n- Reset Time: {data["priority"]["reset"]}\n- Time Recorded: {data["priority"]["time_recorded"]}\n\n**MULTI**\n- Remaining: {data["multi"]["remaining"]}\n- Limit: {data["multi"]["limit"]}\n- Reset Time: {data["multi"]["reset"]}\n- Time Recorded: {data["multi"]["time_recorded"]}')

  # Restarts the bot
  @commands.command()
  async def restart(self, ctx):
    info = await self.bot.application_info() # Checks if user is the bot's owner
    if ctx.author.id == info.owner.id:
      await ctx.reply("Restarting...")
      await ctx.message.delete()
      os.system("kill 1")
      os.execv(sys.executable, ['python'] + sys.argv)
  

# COG SETUP
async def setup(bot):
  await bot.add_cog(monitor(bot))