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


def init_logger(level=INFO):
    """Initialize the logger and sets it to the level specified

    Keyword Arguments:
        level {int} -- Level of the logger (default: {INFO})
    """
    discord_logger = getLogger("discord")
    discord_logger.setLevel(level)
    root_logger = getLogger()
    root_logger.setLevel(level)
    handler = FileHandler(filename="/brisebois/log/bot.log", encoding="utf-8", mode="w")
    root_logger.addHandler(handler)


def get_token():
    """Get the Discord tokoen from MongoDB

    Returns:
        str -- Discord Token
    """
    client = MongoClient()
    database = client.brisebois.api_keys
    entry = database.find_one({"discord": {"$exists": True}})
    return entry["discord"]


@BOT.event
async def on_ready():
    """Called when the bot starts"""
    info('Logged in as:')
    info('Username: ' + BOT.user.name)
    info('ID: ' + BOT.user.id)
    info('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.utcnow()


@BOT.event
async def on_command_error(ctx, error):
    """Called when a command send an error"""
    if isinstance(error, errors.NoPrivateMessage):
        await ctx.author.send("This command cannot be used in private messages.")
    elif isinstance(error, errors.CommandOnCooldown):
        await ctx.author.send(
            "This command is on cooldown, retry after {} seconds".format(
                error.retry_after))
    elif isinstance(error, errors.DisabledCommand):
        await ctx.author.send("This command is disabled and cannot be used.")
    elif isinstance(error, errors.CommandNotFound):
        await ctx.author.send("Unknown command. Use $help to get commands")
        await ctx.message.delete()
    elif isinstance(error, errors.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=stderr)
        print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original),
              file=stderr)


if __name__ == '__main__':
    init_logger(INFO)
    # Add support for netcat and wait for MongoDB before it starts
    for extension in EXTENSIONS:
        try:
            BOT.load_extension(extension)
        except ImportError as err:
            exc = '{}: {}'.format(type(err).__name__, err)
            critical('Failed to load extension {}\n{}'.format(extension, exc))

    TOKEN = get_token()
    BOT.run(TOKEN)
