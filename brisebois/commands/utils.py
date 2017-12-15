#!/bin/env python

"""Utils Commands and Functions module"""

from logging import info
from discord.ext import commands


class Utils(object):
    """Implements Utils commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def admin(self, ctx):
        """Administrative function"""
        if ctx.invoked_subcommand is None:
            await ctx.channel.send("No subcommand specified\nUse `{}help {}` to see the list of commands.".format(ctx.prefix, ctx.command))
            await ctx.message.delete()

    @admin.command()
    async def enable(self, ctx, *command):
        """Enables a command"""
        cmd = self.bot.get_command(" ".join(command))
        cmd.enabled = True
        await ctx.author.send("{} command enabled".format(command))

    @admin.command()
    async def disable(self, ctx, *command):
        """Disables a command"""
        cmd = self.bot.get_command(" ".join(command))
        cmd.enabled = False
        await ctx.author.send("{} command disabled".format(command))

    @admin.command()
    async def prefix(self, ctx, prefix):
        """Changes the prefix of commands"""
        self.bot.command_prefix = prefix
        await ctx.channel.send("Prefix has been changed to {}".format(prefix))

    @admin.command()
    async def load(self, ctx, extension_name):
        """Loads an extension"""
        extension_name = "commands." + extension_name
        try:
            self.bot.load_extension(extension_name)
            await ctx.author.send("{} loaded.".format(extension_name))
        except(AttributeError, ImportError) as err:
            await ctx.author.send("```py\n{}: {}\n```" .format(type(err).__name__, str(err)))

    @admin.command()
    async def unload(self, ctx, extension_name):
        """Unloads an extension"""
        extension_name = "commands." + extension_name
        self.bot.unload_extension(extension_name)
        await ctx.author.send("{} unloaded.".format(extension_name))

    @admin.command()
    async def reload(self, ctx, extension_name):
        """Reloads an extension"""
        extension_name = "commands." + extension_name
        try:
            self.bot.unload_extension(extension_name)
            self.bot.load_extension(extension_name)
            await ctx.author.send("{} reloaded".format(extension_name))
        except (AttributeError, ImportError) as err:
            await ctx.author.send("```py\n{}: {}\n```" .format(type(err).__name__, str(err)))

    @admin.command()
    async def list(self, ctx):
        """List extensions loaded"""
        await ctx.author.send("Commands loaded : {}".format(", ".join(self.bot.cogs)))


def setup(bot):
    """Add commands to the bot"""
    bot.add_cog(Utils(bot))
