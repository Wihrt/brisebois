#!/bin/env python

"""Brisebois Discord Bot"""

# Imports
from logging import getLogger, FileHandler, StreamHandler, info, critical, INFO
from os import environ
from sys import stdout, stderr
from traceback import print_tb

from classes.botmongo import BotMongo
from discord import Color, Embed
from discord.ext.commands import errors

# Create the bot
BOT = BotMongo(command_prefix="$", pm_help=False,
               mongo_host=environ["MONGO_HOST"],
               mongo_port=int(environ["MONGO_PORT"]))
# Extensions to load
EXTENSIONS = ["commands.fun",
              "commands.guess",
              "commands.rng",
              "commands.utils",
              "commands.weather"]


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
    """Called when the bot starts"""
    info('Logged in as:')
    info('Username: ' + BOT.user.name)
    info('ID: ' + BOT.user.id)
    info('------')


@BOT.event
async def on_command_error(ctx, error):
    """Called when a command send an error"""
    message = Embed(color=Color.dark_red())
    if isinstance(error, errors.NoPrivateMessage):
        text = ":warning: This command cannot be used in private messages."
    elif isinstance(error, errors.CommandOnCooldown):
        text = ":stopwatch: This command is on cooldown, retry after {:.2f} seconds".format(error.retry_after)
    elif isinstance(error, errors.DisabledCommand):
        text = "This command is disabled and cannot be used."
    elif isinstance(error, errors.CommandNotFound):
        text = ":grey_question: Unknown command. Use `{}help` to get commands".format(ctx.prefix)
    elif isinstance(error, errors.CommandInvokeError):
        text = ":stop_sign: The command has thrown an error. Use `{}help {}` to see how to use it.".format(ctx.prefix, ctx.command)
        critical('In {0.command.qualified_name}:'.format(ctx), file=stderr)
        print_tb(error.original.__traceback__)
        critical('{0.__class__.__name__}: {0}'.format(error.original),file=stderr)
    message.add_field(name="Error", value=text, inline=False)
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
