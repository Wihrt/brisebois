#!/bin/env python
from datetime import datetime
from discord.ext.commands.bot import Bot
from logging import getLogger, FileHandler, info, DEBUG, INFO
from os import listdir
from os.path import splitext
from pymongo import MongoClient
from sys import stderr
from traceback import print_tb
import discord.ext.commands.errors as err

# Logging
discord_logger = getLogger('discord')
# discord_logger.setLevel(DEBUG)
discord_logger.setLevel(INFO)
log = getLogger()
# log.setLevel(DEBUG)
log.setLevel(INFO)
handler = FileHandler(filename='brisebois.log', encoding='utf-8', mode='w')
log.addHandler(handler)


# Create the bot
bot = Bot(command_prefix="$", pm_help=True)


@bot.event
async def on_ready():
    info('Logged in as:')
    info('Username: ' + bot.user.name)
    info('ID: ' + bot.user.id)
    info('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.utcnow()


@bot.event
async def on_command(command, ctx):
    info("Command : {0.command} called".format(ctx))
    info("Message : {0.content}".format(ctx.message))


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, err.NoPrivateMessage):
        await bot.send_message(
            ctx.message.author,
            "This command cannot be used in private messages.")
    elif isinstance(error, err.CommandOnCooldown):
        await bot.send_message(
            ctx.message.author,
            "This command is on cooldown, retry after {} seconds".format(
                error.retry_after))
    elif isinstance(error, err.DisabledCommand):
        await bot.send_message(
            ctx.message.author,
            "Sorry. This command is disabled and cannot be used.")
    elif isinstance(error, err.CommandNotFound):
        await bot.send_message(
            ctx.message.author,
            "No command {} is found\n\
Use $help to see the list of commands".format(ctx.message.content))
        await bot.delete_message(ctx.message)
    elif isinstance(error, err.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=stderr)
        print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original),
              file=stderr)


@bot.event
async def on_member_join(member):
        server = member.server
        fmt = "Welcome {0.mention} to {1.name} !"
        await bot.send_message(server, fmt.format(member, server))


if __name__ == '__main__':
    commands_dir = "commands"
    for f in listdir(commands_dir):
        try:
            if not f.startswith("_"):
                extension = "%s.%s" % (commands_dir, splitext(f)[0])
                bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

        client = MongoClient()
        db = client.brisebois.api_keys
        entry = db.find_one({"discord": {"$exists": True}})
        token = entry["discord"]

    bot.run(token)
