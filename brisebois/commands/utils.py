#!/bin/env python

"""Utils Commands and Functions module"""

from datetime import datetime
from discord.ext import commands


class Utils(object):
    """Implements Utils commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def cmd(self, ctx):
        """Administrative function"""
        if ctx.invoked_subcommand is None:
            await ctx.channel.send("No subcommand specified\nUse `{}help {}` to see the list of commands.".format(ctx.prefix, ctx.command))
            await ctx.message.delete()

    @cmd.command()
    async def load(self, ctx, extension_name):
        """Loads an extension"""
        extension_name = "commands." + extension_name
        try:
            self.bot.load_extension(extension_name)
            await ctx.author.send("{} loaded.".format(extension_name))
        except(AttributeError, ImportError) as err:
            await ctx.author.send("```py\n{}: {}\n```" .format(type(err).__name__, str(err)))

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
            await ctx.author.send("{} reloaded".format(extension_name))
        except (AttributeError, ImportError) as err:
            await ctx.author.send("```py\n{}: {}\n```" .format(type(err).__name__, str(err)))

    @cmd.command()
    async def list(self, ctx):
        """List extensions loaded"""
        await ctx.author.send("Commands loaded : {}".format(", ".join(self.bot.cogs)))


def setup(bot):
    """Add commands to the bot"""
    bot.add_cog(Utils(bot))