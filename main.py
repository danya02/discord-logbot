import discord
from discord.ext import commands
from cogs import cog_list
import os

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!@#$%^!@#$%^', help_command=None)

for cog in cog_list:
    bot.add_cog( cog(bot) )

bot.run(TOKEN)
