from database import GuildMemberJoinTimeSeries
from discord.ext import commands
from .common import *

class GuildMemberJoinTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @requires_feature('MEMBER_JOIN', lambda args, kwargs: args[1].guild.id)
    async def on_member_join(self, member):
        await asyncify(GuildMemberJoinTimeSeries.create, guild_id=member.guild.id, member_id=member.id, is_joining=True)
    
    @commands.Cog.listener()
    @requires_feature('MEMBER_JOIN', lambda args, kwargs: args[1].guild.id)
    async def on_member_remove(self, member):
        await asyncify(GuildMemberJoinTimeSeries.create, guild_id=member.guild.id, member_id=member.id, is_joining=False)
