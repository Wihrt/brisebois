#!/bin/env python
from discord.ext.commands.bot import Bot
import discord

# Constants
# -----------------------------------------------------------------------------

TOKEN_FILE = "token.txt"
EXTENSIONS = ["commands.fun", "commands.sound"]

# Create the bot
bot = Bot(command_prefix="$", pm_help=True)


@bot.event
async def on_ready():
    print("Logged in as %s" % bot.user.name)


@bot.command(hidden=True)
async def load(extension_name):
    """Load an extension."""
    try:
        bot.load_extension(extension_name)
    except(AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))


@bot.command(hidden=True)
async def unload(extension_name):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))


@bot.command(hidden=True):
async def reload(extension_name):
    """Reload an extension."""
    try:
	bot.unload_extension(extension_name)
	bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
	await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
    await bot.say("{} reloaded".format(extension_name)

if __name__ == '__main__':
    for extension in EXTENSIONS:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    with open(TOKEN_FILE, "r") as f:
        token = f.readlines()

    bot.run(token)
