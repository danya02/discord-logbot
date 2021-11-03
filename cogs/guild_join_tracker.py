from database import GuildJoinTimeSeries
from discord.ext import commands

class GuildJoinTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        GuildJoinTimeSeries.create(guild_id=guild.id, is_joining=True)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        GuildJoinTimeSeries.create(guild_id=guild.id, is_joining=False)
