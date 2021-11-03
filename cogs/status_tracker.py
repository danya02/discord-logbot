from database import BotReadyTimeSeries
from discord.ext import commands, tasks
from .common import *

INTERVAL = 10

class StatusTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_loop.start()

    @tasks.loop(seconds=INTERVAL)
    async def check_loop(self):
        await asyncify( BotReadyTimeSeries.record_status, self.bot.is_ready(), INTERVAL )

