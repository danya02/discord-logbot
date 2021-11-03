import peewee as pw
from typing import Union
from discord.ext.commands import Context

db = pw.SqliteDatabase('/data.db')

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
        return feature_name in guild_settings.features.split():


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

