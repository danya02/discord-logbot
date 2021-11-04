import asyncio
from typing import Tuple, Sequence, Mapping, Any, Callable
import functools
import database
import logging

logging.basicConfig(level=logging.DEBUG)

async def asyncify(func, *args, **kwargs):
    """Thin wrapper around `asyncio.to_thread`."""
    coro = asyncio.to_thread(func, *args, **kwargs)
    result = await coro
    return result

def requires_feature(feature_name: str, how_to_get_guild_id: Callable[ [Sequence[Any], Mapping[str, Any]], int ]):
    """
    Decorator that only calls the decorated function if the specified feature is enabled in the guild.
    The decorated function must be an async function.

    `feature_name` is the name of the feature that needs to be enabled.
    `how_to_get_guild_id` is a function that takes the `args` tuple and the `kwargs` dict, and returns the ID of the guild for which this event has occurred.
    """
    logging.debug(f"Decorating `requires_feature` with feature_name: {feature_name} and how_to_get_guild_id: {how_to_get_guild_id}")

    def decorator(function):
        @functools.wraps(function)
        async def decorated(*args, **kwargs):
            logging.debug(f"Running `requires_feature`-decorated function for {feature_name} with {args} and {kwargs}")
            guild_id = how_to_get_guild_id(args, kwargs)
            should_run = await asyncify(database.GuildSettings.is_feature_enabled, guild_id, feature_name)
            if should_run:
                logging.debug(f"Condition for running in guild {guild_id} met")
                return await function(*args, **kwargs)
            else:
                logging.debug(f"Condition for running in guild {guild_id} not met")
        return decorated
    return decorator
