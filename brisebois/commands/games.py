#!/bin/env python

"""Games Commands module"""

from html import unescape
from random import shuffle

from utils.embed import create_embed

from discord import Color
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from requests import get

class Games(object):
    """Implements Games commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, "15.0", BucketType.guild)
    async def trivia(self, ctx):
        """Give a random trivia question"""
        def _is_answer(msg):
            return msg.content.isdigit()

        correct, answers, field = self._trivia("https://opentdb.com/api.php?amount=1")
        message = create_embed(fields=[field])
        await ctx.channel.send(embed=message)
        try:
            msg = await self.bot.wait_for("message", check=_is_answer, timeout=15.0)
        except TimeoutError:
            content = dict(color=Color.red(), fields=[dict(name="Sorry !", value="You took too long to answer !", inline=False)])
        else:
            if answers[int(msg.content) - 1] != correct:
                content = dict(color=Color.red(), fields=[dict(name="Incorrect !", value="The right answer was {}".format(correct), inline=False)])
            else:
                content = dict(color=Color.green(), title="Correct !")
        message = create_embed(**content)
        await ctx.channel.send(embed=message)

    @staticmethod
    def _trivia(url):
        response = get(url)
        response.raise_for_status()
        json = response.json()["results"][0]
        correct_answer = unescape(json["correct_answer"])
        answers = json["incorrect_answers"] + [correct_answer]
        answers = [unescape(a) for a in answers]
        shuffle(answers)

        msg, i = str(), 1
        for answer in answers:
            msg += "**{}.** {}\n".format(i, answer)
            i += 1
        return correct_answer, answers, dict(name=unescape(json["question"]), value=msg, inline=False)


def setup(bot):
    """Add commands to the Bot"""
    bot.add_cog(Games(bot))
