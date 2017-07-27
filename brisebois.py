#!/bin/env python

"""Brisebois Discord Bot"""

# Imports
from datetime import datetime
from logging import getLogger, FileHandler, info, critical, INFO
from sys import stderr
from traceback import print_tb

from discord.ext.commands import bot, errors
from pymongo import MongoClient

# Create the bot
BOT = bot.Bot(command_prefix="$", pm_help=True)
# Extensions to load
EXTENSIONS = ["commands.fun",
              "commands.guess",
              "commands.quote",
              "commands.rng",
              "commands.utils",
              "commands.weather"]


def init_logger(level: int) -> None:
    """Set the logging of the bot

    Args:
        level: Level of the logging

    Returns:
        None
    """
    discord_logger = getLogger("discord")
    discord_logger.setLevel(level)
    root_logger = getLogger()
    root_logger.setLevel(level)
    handler = FileHandler(filename="brisebois.log", encoding="utf-8", mode="w")
    root_logger.addHandler(handler)


def get_token() -> str:
    """Gets the Token for Discord

    Args:

    Returns:
        str: Token of the bot
    """
    client = MongoClient()
    database = client.brisebois.api_keys
    entry = database.find_one({"discord": {"$exists": True}})
    return entry["discord"]


@BOT.event
async def on_ready() -> None:
    """Called when bot starts.

    Args:

    Returns:
        None
    """
    info('Logged in as:')
    info('Username: ' + BOT.user.name)
    info('ID: ' + BOT.user.id)
    info('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.utcnow()


@BOT.event
async def on_command(command, ctx) -> None:
    """Called when command is sent.

    Args:
        command: Command in the message
        ctx: Context of the message

    Returns:
        None
    """
    info("Message : {0.content}".format(ctx.message))


@BOT.event
async def on_command_error(error, ctx) -> None:
    """Called when command throws an exception.

    Args:
        error: Exception sent by the command
        ctx: Content of the message

    Returns:
        None
    """
    if isinstance(error, errors.NoPrivateMessage):
        await BOT.send_message(
            ctx.message.author,
            "This command cannot be used in private messages.")
    elif isinstance(error, errors.CommandOnCooldown):
        await BOT.send_message(
            ctx.message.author,
            "This command is on cooldown, retry after {} seconds".format(
                error.retry_after))
    elif isinstance(error, errors.DisabledCommand):
        await BOT.send_message(
            ctx.message.author,
            "Sorry. This command is disabled and cannot be used.")
    elif isinstance(error, errors.CommandNotFound):
        await BOT.send_message(
            ctx.message.author,
            "No command {} is found\n\
Use $help to see the list of commands".format(ctx.message.content))
        await BOT.delete_message(ctx.message)
    elif isinstance(error, errors.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=stderr)
        print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original),
              file=stderr)


if __name__ == '__main__':
    init_logger(INFO)
    for extension in EXTENSIONS:
        try:
            BOT.load_extension(extension)
        except ImportError as err:
            exc = '{}: {}'.format(type(err).__name__, err)
            critical('Failed to load extension {}\n{}'.format(extension, exc))

    TOKEN = get_token()
    BOT.run(TOKEN)
