#!/bin/env python

"""Guess Commands module"""

from asyncio import TimeoutError
from html import unescape
from random import shuffle

from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from requests import get


class Guess(object):
    """Implements Guess commands"""

    def __init__(self, bot):
        self.bot = bot   

    @commands.command()
    @commands.cooldown(1, "15.0", BucketType.guild)
    async def trivia(self, ctx):
        """Give a random trivia question"""
        def _is_answer(msg):
            return msg.content.isdigit()

        def _format_answers(answers):
            message, i = str(), 1
            for answer in answers:
                message += "**%s.** %s\n" % (i, answer)
                i += 1
            return message

        json = get("https://opentdb.com/api.php?amount=1").json()["results"][0]
        correct_answer = unescape(json["correct_answer"])
        answers = json["incorrect_answers"] + [correct_answer]
        answers = [unescape(a) for a in answers]
        shuffle(answers)

        message = Embed()
        message.add_field(name=unescape(json["question"]),
                          value=_format_answers(answers),
                          inline=False)
        await ctx.channel.send(embed=message)
        try:
            msg = await self.bot.wait_for("message", check=_is_answer, timeout=15.0)
        except TimeoutError:
            message = Embed(color=Color.red())
            message.add_field(name="Sorry !",
                              value="You took too long to answer !",
                              inline=False)
        else:
            if answers[int(msg.content) - 1] != correct_answer:
                message = Embed(color=Color.red())
                message.add_field(name="Incorrect !",
                                  value="The right answer was %s" %
                                  correct_answer,
                                  inline=False)
            else:
                message = Embed(color=Color.green(), title="Correct !")
        await ctx.channel.send(embed=message)
        return


def setup(bot):
    bot.add_cog(Guess(bot))
