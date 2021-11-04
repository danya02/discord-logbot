import discord
from discord.ext import commands
from cogs import cog_list
import os

import logging
logging.basicConfig(level=logging.DEBUG)

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!@#$%^!@#$%^', help_command=None, intents=intents)

for cog in cog_list:
    bot.add_cog( cog(bot) )

bot.run(TOKEN)
