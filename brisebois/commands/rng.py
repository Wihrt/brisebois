#!/bin/env python

"""RNG Commands module"""


from discord.ext import commands
import dice


class Rng(object):  # pylint: disable=too-few-public-methods
    """Implements RNG commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dice(self, ctx, message):
        """Roll a dice
        Exemple : $dice 3d6"""
        result = dice.roll(message)
        if isinstance(result, list):
            result = sum(result)
        await ctx.channel.send("Roll {0} = {1}".format(message, result))


def setup(bot):
    """Add commands to the bot.

    Args:
        bot: Bot which will add the commands

    Returns:
        None
    """
    bot.add_cog(Rng(bot))
