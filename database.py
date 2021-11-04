import peewee as pw
from typing import Union
from discord.ext.commands import Context
import datetime

db = pw.SqliteDatabase('./data.db')

class MyModel(pw.Model):
    class Meta:
        database = db

def create_table(cls):
    db.create_tables([cls])
    return cls

@create_table
class GuildSettings(MyModel):
    guild_id = pw.BigIntegerField(unique=True)
    features = pw.TextField(default='')

    @classmethod
    def is_feature_enabled(cls, ctx: Union[Context, int], feature_name: str) -> bool:
        """
        Return whether `feature_name` is enabled in the guild described by `ctx`.

        `ctx` can either be a `discord.ext.commands.Context` or an `int` -- if it's
        the latter, it is interpreted as the guild's ID.
        """

        if isinstance(ctx, int):
            guild_id = ctx
        else:
            guild_id = ctx.guild.id
        guild_settings, _ = cls.get_or_create(guild_id=guild_id)
        return feature_name in guild_settings.features.split() or 'EVERYTHING' in guild_settings.features.split()


    @classmethod
    def set_feature_enabled(cls, ctx: Union[Context, int], feature_name: str, enabled: bool) -> None:
        """
        Set `feature_name` to be `enabled` (True for on, False for off) in the guild by `ctx`. `ctx` is interpreted the same way as in `is_feature_enabled`.
        """
        if isinstance(ctx, int):
            guild_id = ctx
        else:
            guild_id = ctx.guild.id
        guild_settings, _ = cls.get_or_create(guild_id=guild_id)
        current_features = set(guild_settings.features.split())
        if enabled:
            current_features.add(feature_name)
        else:
            current_features.discard(feature_name)
        guild_settings.features = '\n'.join(current_features)

class TimeSeries(MyModel):
    when = pw.DateTimeField(default=datetime.datetime.now, index=True)

@create_table
class BotReadyTimeSeries(TimeSeries):
    is_ready = pw.BooleanField()
    state_stable_for_seconds = pw.DoubleField(default=0, index=True)

    @classmethod
    def record_status(cls, status: bool, loop_interval: float, time_margin=3) -> None:
        """ Record the current status of the bot, and automatically deduplicate entries. """
        
        try:
            last_record = cls.select().order_by(-cls.when).get()
        except cls.DoesNotExist:
            cls.create(is_ready=status)
            return

        if status != last_record.is_ready:
            # Status changed within last loop, so we say that starting from the last loop the status is the new one.
            last_record_ended_at = last_record.when + datetime.timedelta(seconds=last_record.state_stable_for_seconds)
            cls.create(when=last_record_ended_at, is_ready=status)
            return

        # last record is the same status as current one -- is the last record stale?
        now = datetime.datetime.now()
        
        # this is the time that we last recorded this status
        last_record_for_status = last_record.when + datetime.timedelta(seconds=last_record.state_stable_for_seconds)
        elapsed = now - last_record_for_status  # this is how long it has been since the last record of status
        elapsed_seconds = elapsed.total_seconds()
        if elapsed_seconds > (loop_interval + time_margin):
            # yes, the status is stale -- creating record for all time not accounted for
            cls.create(is_ready=False,  # if we were not recording status, we were offline
                    when=last_record_for_status,  # we were offline since the last recorded status
                    state_stable_for_seconds = (now - last_record.when).total_seconds() )  # and the offline duration is the time between the start and now

            # now there is an event that has been last recorded right now, so call myself recursively
            # if the current status is False, it will extend it until now
            # if the current status is True, it will record a new one
            cls.record_status(status, loop_interval, time_margin)

        else:
            # no, the status is not stale, so extend it until now
            last_record.state_stable_for_seconds = (now - last_record.when).total_seconds()
            last_record.save()

            # for some reason, this algorithm misses several zero-length events when starting for the first time.
            # if we are stable, this is a good time to clean those up.
            cls.delete().where(cls.state_stable_for_seconds == 0).execute()



@create_table
class GuildJoinTimeSeries(TimeSeries):
    guild_id = pw.BigIntegerField()
    is_joining = pw.BooleanField()

@create_table
class GuildMemberJoinTimeSeries(TimeSeries):
    guild_id = pw.BigIntegerField()
    member_id = pw.BigIntegerField()
    is_joining = pw.BooleanField()

@create_table
class GuildMemberBanTimeSeries(TimeSeries):
    guild_id = pw.BigIntegerField()
    member_id = pw.BigIntegerField()
    is_banned = pw.BooleanField()

@create_table
class GuildInviteTimeSeries(TimeSeries):
    is_creating = pw.BooleanField()
    guild_id = pw.BigIntegerField()
    channel_id = pw.BigIntegerField()
    code = pw.CharField()
    max_age = pw.BooleanField(null=True)
    revoked = pw.BooleanField(null=True)
    created_at_recv = pw.DateTimeField(null=True)
    temporary = pw.BooleanField(null=True)
    uses = pw.IntegerField(null=True)
    max_uses = pw.IntegerField(null=True)
    inviter_id = pw.BigIntegerField(null=True)


    
