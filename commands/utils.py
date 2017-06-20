#!/bin/env python
from discord.ext import commands


class Utils(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True,
                    hidden=True)
    async def cmd(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(
                ctx.message.author,
                "No subcommand specified\n\
Use $help %s to see the list of commands." % ctx.command)
            await self.bot.delete_message(ctx.message)

    @cmd.command(name="load",
                 pass_context=True,
                 help="Load an extension")
    async def _load(self, ctx, extension_name):
        extension_name = "commands." + extension_name
        try:
            self.bot.load_extension(extension_name)
        except(AttributeError, ImportError) as e:
            await self.bot.say("```py\n%s: %s\n```" %
                               (type(e).__name__, str(e)))
            return
        await self.bot.say("{} loaded.".format(extension_name))
        return

    @cmd.command(name="unload",
                 pass_context=True,
                 help="Unload an extension")
    async def _unload(self, ctx, extension_name):
        extension_name = "commands." + extension_name
        self.bot.unload_extension(extension_name)
        await self.bot.say("{} unloaded.".format(extension_name))
        return

    @cmd.command(name="reload",
                 pass_context=True,
                 help="Reload an extension")
    async def _reload(self, ctx, extension_name):
        extension_name = "commands." + extension_name
        try:
            self.bot.unload_extension(extension_name)
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            await self.bot.say("```py\n%s: %s\n```" %
                               (type(e).__name__, str(e)))
            return
        await self.bot.say("{} reloaded".format(extension_name))
        return

    @cmd.command(name="list",
                 pass_context=True,
                 help="List extensions loaded")
    async def _list(self, ctx):
        await self.bot.say("Commands loaded : %s" % ", ".join(self.bot.cogs))
        return


def setup(bot):
    bot.add_cog(Utils(bot))
