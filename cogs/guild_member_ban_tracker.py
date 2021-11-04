from database import GuildMemberBanTimeSeries
from discord.ext import commands
from .common import *

class GuildMemberBanTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @requires_feature('MEMBER_BAN', lambda args, kwargs: args[1].id)
    async def on_member_ban(self, guild, member):
        await asyncify(GuildMemberBanTimeSeries.create, guild_id=guild.id, member_id=member.id, is_banned=True)
    
    @commands.Cog.listener()
    @requires_feature('MEMBER_BAN', lambda args, kwargs: args[1].id)
    async def on_member_unban(self, guild, member):
        await asyncify(GuildMemberBanTimeSeries.create, guild_id=guild.id, member_id=member.id, is_banned=False)
