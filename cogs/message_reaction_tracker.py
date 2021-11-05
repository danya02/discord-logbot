from database import MessageReactionTimeSeries, MessageReactionEvent
from discord.ext import commands
import discord
from .common import *

class MessageReactionTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @requires_feature('MESSAGE_REACTION', lambda args, kwargs: args[1].guild_id)
    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji
        await asyncify(MessageReactionTimeSeries.create,
                guild_id=payload.guild_id,
                channel_id=payload.channel_id,
                message_id=payload.message_id,
                reaction = (emoji.name if emoji.is_unicode_emoji() else str(emoji.id)),
                reaction_owner_id=payload.user_id,
                event=MessageReactionEvent.ADD)

    @commands.Cog.listener()
    @requires_feature('MESSAGE_REACTION', lambda args, kwargs: args[1].guild_id)
    async def on_raw_reaction_remove(self, payload):
        emoji = payload.emoji
        await asyncify(MessageReactionTimeSeries.create,
                guild_id=payload.guild_id,
                channel_id=payload.channel_id,
                message_id=payload.message_id,
                reaction = (emoji.name if emoji.is_unicode_emoji() else str(emoji.id)),
                reaction_owner_id=payload.user_id,
                event=MessageReactionEvent.REMOVE)

    @commands.Cog.listener()
    @requires_feature('MESSAGE_REACTION', lambda args, kwargs: args[1].guild_id)
    async def on_raw_reaction_clear_emoji(self, payload):
        emoji = payload.emoji
        await asyncify(MessageReactionTimeSeries.create,
                guild_id=payload.guild_id,
                channel_id=payload.channel_id,
                message_id=payload.message_id,
                reaction = (emoji.name if emoji.is_unicode_emoji() else str(emoji.id)),
                reaction_owner_id=None,
                event=MessageReactionEvent.CLEAR_EMOJI)
    
    @commands.Cog.listener()
    @requires_feature('MESSAGE_REACTION', lambda args, kwargs: args[1].guild_id)
    async def on_raw_reaction_clear(self, payload):
        await asyncify(MessageReactionTimeSeries.create,
                guild_id=payload.guild_id,
                channel_id=payload.channel_id,
                message_id=payload.message_id,
                reaction = None,
                reaction_owner_id=None,
                event=MessageReactionEvent.CLEAR_ALL)
