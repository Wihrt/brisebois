#!/bin/env python

"""Utils Commands and Functions module"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from discord.ext import commands


class Utils(object):
    """Implements Utils commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def cmd(self, ctx):
        """Administrative function"""
        await self.bot.delete_message(ctx.message)
        if ctx.invoked_subcommand is None:
            await ctx.channel.send("No subcommand specified\n\
Use `{}help {}` to see the list of commands.".format(ctx.prefix, ctx.command))
            await ctx.message.delete()

    @cmd.command()
    async def load(self, ctx, extension_name):
        """Loads an extension"""
        extension_name = "commands." + extension_name
        try:
            self.bot.load_extension(extension_name)
            await ctx.author.send("{} loaded.".format(extension_name))
        except(AttributeError, ImportError) as err:
            await ctx.author.send("```py\n%s: %s\n```" %
                                  (type(err).__name__, str(err)))

    @cmd.command()
    async def unload(self, ctx, extension_name):
        """Unloads an extension"""
        extension_name = "commands." + extension_name
        self.bot.unload_extension(extension_name)
        await ctx.author.send("{} unloaded.".format(extension_name))

    @cmd.command()
    async def reload(self, ctx, extension_name):
        """Reloads an extension"""
        extension_name = "commands." + extension_name
        try:
            self.bot.unload_extension(extension_name)
            self.bot.load_extension(extension_name)
            await self.bot.whisper("{} reloaded".format(extension_name))
        except (AttributeError, ImportError) as err:
            await ctx.author.send("```py\n%s: %s\n```" %
                                  (type(err).__name__, str(err)))

    @cmd.command()
    async def list(self, ctx):
        """List extensions loaded"""
        await ctx.author.send("Commands loaded : %s" %
                              ", ".join(self.bot.cogs))


def setup(bot):
    """Add commands to the bot.

    Args:
        bot: Bot which will add the commands

    Returns:
        None
    """
    bot.add_cog(Utils(bot))


# Date related functions
def date_create(days=0, months=0):
    """Create the UTC date

    Args:
        days (int): Days to add to the current date
        months (int): Months to add to the current date

    Return: date
    """
    return datetime.utcnow() + relativedelta(days=days, months=months)


def date_check(date, fmt="%Y-%m-%d"):
    """Checks the date format

    Args:
        fmt (str): Date format

    Return: bool
    """
    try:
        datetime.strptime(date, fmt)
        return True
    except (TypeError, ValueError):
        return False


def date_range(date=None, fmt="%Y-%m-%d"):
    """Create the date range for the date

    Args:
        date (date): Date to use as reference
        fmt (str): Format of the date

    Return: (date, date)
    """
    if date_check(date, fmt):
        date = datetime.strptime(date, fmt)
    else:
        date = datetime.utcnow()

    start_date = date.replace(hour=0, minute=0, second=0)
    end_date = date.replace(hour=23, minute=59, second=59)
    return (start_date, end_date)


def date_compare(date, reference):
    """Checks the date is superior to the reference

    Args:
        date (date): Date to check
        reference (date): Reference to check

    Return: bool
    """
    if date < reference:
        return True
    return False
