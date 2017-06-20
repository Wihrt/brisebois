#!/bin/env python
from discord.ext.commands.bot import Bot
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
        await bot.delete_message(ctx.message)
        await bot.send_message(
            ctx.message.author,
            "This command is on cooldown, retry after : %i seconds" %
            error.retry_after)
    elif isinstance(error, err.CommandNotFound):
        await bot.send_message(
            ctx.message.author,
            "No command %s is found\nUse $help to see the list of commands" %
            ctx.message.content)
        await bot.delete_message(ctx.message)
    else:
        print('Ignoring exception in command {}'.format(ctx.command),
              file=stderr)
        print_exception(type(error), error, error.__traceback__, file=stderr)


if __name__ == '__main__':
    for f in listdir(COMMANDS_DIR):
        try:
            if not f.startswith("__"):
                extension = "%s.%s" % (COMMANDS_DIR, splitext(f)[0])
                bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    with open(TOKEN_FILE, "r") as f:
        token = f.readline()

    bot.run(token)
