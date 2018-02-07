#!/bin/env python

"""RPG Commands module"""

from discord.ext import commands
import dice


class Rpg(object):
    """Implements RPG commands"""

    def __init__(self, bot):
        self.bot = bot

    # Commands
    # -------------------------------------------------------------------------
    @commands.command()
    @commands.guild_only()
    async def dice(self, ctx, *, msg):
        """Roll a dice

        Decorators:
            commands

        Arguments:
            ctx {Context} -- Context of the message
            msg {str} -- Dice to roll
        """
        result = dice.roll(msg)
        if isinstance(result, list):
            result = sum(result)
        await ctx.channel.send("{} Roll {} = {}".format(ctx.author.mention, msg, result))

def setup(bot):
    """Add RPG commands to the Bot"""
    bot.add_cog(Rpg(bot))
