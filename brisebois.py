#!/bin/env python
from discord.ext.commands.bot import Bot
from lib.utils import get_key
from os import listdir
from os.path import splitext
from sys import stderr
from traceback import print_exception
import discord.ext.commands.errors as err

# Constants
# -----------------------------------------------------------------------------
TOKEN_FILE = "token.txt"
COMMANDS_DIR = "commands"

# Create the bot
bot = Bot(command_prefix="$",
          pm_help=True)
bot.API_KEYS = "api_keys.json"


@bot.event
async def on_ready():
    print("Logged in as %s" % bot.user.name)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, err.NoPrivateMessage):
        await bot.send_message(
            ctx.message.author,
            "This command cannot be used in private messages.")
    elif isinstance(error, err.CommandOnCooldown):
        await bot.send_message(
            ctx.message.author,
            "This command is on cooldown, retry after : %i seconds" %
            error.retry_after)
        await bot.delete_message(ctx.message)
    elif isinstance(error, err.CommandNotFound):
        await bot.send_message(
            ctx.message.author,
            "No command %s is found\nUse $help to see the list of commands" %
            ctx.message.content)
        await bot.delete_message(ctx.message)
    elif isinstance(error, err.CheckFailure):
        await bot.send_message(
            ctx.message.author,
            "You don't have the roles/permissions to use this command")
    else:
        print('Ignoring exception in command {}'.format(ctx.command),
              file=stderr)
        print_exception(type(error), error, error.__traceback__, file=stderr)


@bot.event
async def on_member_join(member):
        server = member.server
        fmt = "Welcome {0.mention} to {1.name} !"
        await bot.send_message(server, fmt.format(member, server))


if __name__ == '__main__':
    for f in listdir(COMMANDS_DIR):
        try:
            if not f.startswith("__"):
                extension = "%s.%s" % (COMMANDS_DIR, splitext(f)[0])
                bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
        token = get_key(bot.API_KEYS, "discord")

    bot.run(token)
