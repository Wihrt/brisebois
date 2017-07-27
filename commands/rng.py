#!/bin/env python

"""RNG Commands module"""

from random import randint

from discord.ext import commands


class Rng(object):  # pylint: disable=too-few-public-methods
    """Implements RNG commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dice(self, faces=6, number=1):
        """Roll a dice

        Args:
            faces (int): Number of faces of the dice
            number (int): Number of dice

        Return: None
        """

        value = 0
        for dice in range(1, number + 1):
            value += randint(1, faces)
        await self.bot.say("Roll {0}d{1} = {2}".format(number, faces, value))
        return


def setup(bot):
    """Add commands to the bot.

    Args:
        bot: Bot which will add the commands

    Returns:
        None
    """
    bot.add_cog(Rng(bot))
