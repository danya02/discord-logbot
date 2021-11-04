from database import TypingTimeSeries
from discord.ext import commands
import discord
from .common import *

class TypingTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @requires_feature('TYPING', lambda args, kwargs: args[1].guild.id)
    async def on_typing(self, channel, user, when):
        await asyncify(TypingTimeSeries.create, guild_id=(channel.guild.id if isinstance(channel, discord.TextChannel) else None), channel_id=channel.id, member_id=user.id, when=when)
    
