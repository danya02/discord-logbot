import peewee as pw
from typing import Union
from discord.ext.commands import Context
import datetime
from enum import Enum
import logging

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
        
        logging.debug(f"Recording current state as {status}")

        try:
            last_record = cls.select().order_by(-cls.when).get()
        except cls.DoesNotExist:
            # if there were no records found, this is the first one, so just record this status
            cls.create(is_ready=status)
            return

        now = datetime.datetime.now()
        time_since_last_record_started = (now - last_record.when).total_seconds()
        last_record_ended_at = last_record.when + datetime.timedelta(seconds=last_record.state_stable_for_seconds)
        time_since_last_record_ended = (now - last_record_ended_at).total_seconds()
        logging.debug(f"Last record ended {time_since_last_record_ended} seconds ago")
        if time_since_last_record_ended > (loop_interval + time_margin):
            logging.debug("That exceeds the outage interval, inserting outage data")
            # we have been offline since the end of the last record until now
            if last_record.is_ready == False:
                logging.debug("Last record is offline, so extending that record by the time left")
                # we have been offline back then too, so we can extend that record until now
                last_record.state_stable_for_seconds = time_since_last_record_started
                last_record.save()
            else:
                logging.debug("Last record is online, creating record starting when that ended")
                # we have been online for the last record, so we need to insert a record for the unaccounted time
                logging.debug(f"Outage started at {last_record_ended_at.isoformat()} and lasted {time_since_last_record_ended}")
                cls.create(is_ready=False, when=last_record_ended_at, state_stable_for_seconds=time_since_last_record_ended)
                cls.create(is_ready=status, when=now)

            # if this is the first record after an outage, then there is no opportunity to extend it.
            return

        # the last record was made within acceptable time margins for extension
        last_record.state_stable_for_seconds = time_since_last_record_started
        last_record.save()

        # is the record of the same value? if it isn't, then the state changed, so we mark it as having changed in this iteration (with zero length -- it'll get extended as needed)
        if last_record.is_ready != status:
            logging.debug(f"Between last log and now, we switched state from {last_record.is_ready} to {status}, so creating {status} record.")
            cls.create(is_ready=status)


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

@create_table
class TypingTimeSeries(TimeSeries):
    guild_id = pw.BigIntegerField(null=True)
    channel_id = pw.BigIntegerField()
    member_id = pw.BigIntegerField()

class MessageReactionEvent(Enum):
    ADD = 1
    REMOVE = 2
    CLEAR_EMOJI = 3
    CLEAR_ALL = 4

class MessageReactionEventField(pw.Field):
    field_type = 'integer'

    def db_value(self, value):
        return str(int(value.value))

    def python_value(self, value):
        return ReactionEvent( int(value) )

@create_table
class MessageReactionTimeSeries(TimeSeries):
    guild_id = pw.BigIntegerField()
    channel_id = pw.BigIntegerField()
    message_id = pw.BigIntegerField()
    reaction = pw.CharField(null=True)
    reaction_owner_id = pw.BigIntegerField(null=True)
    event = MessageReactionEventField()

