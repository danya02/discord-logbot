from database import GuildInviteTimeSeries
from discord.ext import commands
from .common import *

class GuildInviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @requires_feature('INVITE', lambda args, kwargs: args[1].guild.id)
    async def on_invite_create(self, invite):
        await asyncify(GuildInviteTimeSeries.create, is_creating=True,
                guild_id=invite.guild.id, channel_id=invite.channel.id, code=invite.code,
                max_age=invite.max_age, revoked=invite.revoked, created_at_recv=invite.created_at,
                temporary=invite.temporary, uses=invite.uses, max_uses=invite.max_uses,
                inviter_id=(invite.inviter.id if invite.inviter else None))
                
    @commands.Cog.listener()
    @requires_feature('INVITE', lambda args, kwargs: args[1].guild.id)
    async def on_invite_delete(self, invite):
        await asyncify(GuildInviteTimeSeries.create, is_creating=False,
                guild_id=invite.guild.id, channel_id=invite.channel.id, code=invite.code,
                max_age=invite.max_age, revoked=invite.revoked, created_at_recv=invite.created_at,
                temporary=invite.temporary, uses=invite.uses, max_uses=invite.max_uses,
                inviter_id=(invite.inviter.id if invite.inviter else None))
