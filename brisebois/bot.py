#!/bin/env python

"""Brisebois Discord Bot"""

# Imports
from logging import getLogger, FileHandler, StreamHandler, info, critical, INFO
from os import environ
from sys import stdout, stderr
from traceback import print_tb

from utils.botmongo import BotMongo
from utils.embed import create_embed

from discord import Color, Embed
from discord.ext.commands import errors

# Create the bot
# BOT = BotMongo(command_prefix="$", pm_help=False,
#                mongo_host=environ["MONGO_HOST"],
#                mongo_port=int(environ["MONGO_PORT"]))
BOT = BotMongo(command_prefix="$", pm_help=False)
# Extensions to load
EXTENSIONS = ["commands.fun",
              "commands.games",
              "commands.misc",
              "commands.rpg",
              "commands.utils"]


def init_logger(level=INFO):
    """Initialize the logger and sets it to the level specified

    Keyword Arguments:
        level {int} -- Level of the logger (default: {INFO})
    """
    discord = getLogger("discord")
    discord.setLevel(level)
    root = getLogger()
    root.setLevel(level)
    out_handler = StreamHandler(stream=stdout)
    file_handler = FileHandler(filename="log/bot.log", encoding="utf-8", mode="w")
    root.addHandler(out_handler)
    root.addHandler(file_handler)


@BOT.event
async def on_ready():
    info('Logged in as:')
    info('Username: {}'.format(BOT.user.name))
    info('ID: {}'.format(str(BOT.user.id)))
    info('------')


@BOT.event
async def on_command_error(ctx, error):
    content = dict(color=Color.dark_red())
    info(error)
    if isinstance(error, errors.NoPrivateMessage):
        content["fields"] = [dict(name="Error", value=":warning: This command cannot be used in private messages.", inline=False)]
    elif isinstance(error, errors.CommandOnCooldown):
        content["fields"] = [dict(name="Error", value=":stopwatch: This command is on cooldown, retry after {:.2f} seconds".format(error.retry_after), inline=False)]
    elif isinstance(error, errors.DisabledCommand):
        content["fields"] = [dict(name="Error", value="This command is disabled and cannot be used.", inline=False)]
    elif isinstance(error, errors.CommandNotFound):
        content["fields"] = [dict(name="Error", value=":grey_question: Unknown command. Use `{}help` to get commands".format(ctx.prefix), inline=False)]
    elif isinstance(error, errors.MissingPermissions):
        content["fields"] = [dict(name="Error", value=":no_entry_sign: You don't have `{}` to use this command".format(", ").join(error.missing_perms)]
    elif isinstance(error, errors.CommandInvokeError):
        content["fields"] = [dict(name="Error", value=":stop_sign: The command has thrown an error. Use `{}help {}` to see how to use it.".format(ctx.prefix, ctx.command), inline=False)]
        critical('In {0.command.qualified_name}:'.format(ctx))
        print_tb(error.original.__traceback__)
        critical('{0.__class__.__name__}: {0}'.format(error.original))
    message = create_embed(**content)
    await ctx.channel.send(embed=message)


if __name__ == '__main__':
    init_logger(INFO)
    for extension in EXTENSIONS:
        try:
            BOT.load_extension(extension)
        except ImportError as err:
            exc = '{}: {}'.format(type(err).__name__, err)
            critical('Failed to load extension {}\n{}'.format(extension, exc))
    BOT.run(BOT.get_api_key("discord"))
