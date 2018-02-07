#!/bin/env python

"""Games Commands module"""

from asyncio import TimeoutError
from html import unescape
from random import choice, shuffle

from discord import Color
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from utils.embed import create_embed

class Games(object):
    """Implements Games commands"""

    def __init__(self, bot):
        self.bot = bot

    # Commands
    # -------------------------------------------------------------------------
    @commands.command()
    @commands.cooldown(1, "15.0", BucketType.guild)
    @commands.guild_only()
    async def trivia(self, ctx):
        """Send a random trivia question"""
        def _is_answer(msg):
            return msg.content.isdigit()

        response = await self.bot.session.get("https://opentdb.com/api.php?amount=1")
        async with response:
            content = await response.json()
            results = content["results"][0]
            correct = unescape(results["correct_answer"])
            answers = results["incorrect_answers"] + [correct]
            answers = [unescape(a) for a in answers]
            shuffle(answers)

            msg, i = str(), 1
            for answer in answers:
                msg += "**{}.** {}\n".format(i, answer)
                i += 1
            field = dict(name=unescape(results["question"]), value=msg, inline=False)
            message = create_embed(dict(fields=field))
            await ctx.channel.send(embed=message)

            try:
                msg = await self.bot.wait_for("message", check=_is_answer, timeout=15.0)
            except TimeoutError:
                embed = dict(color=Color.red(), \
fields=dict(name="Sorry !", value="You took too long to answer !", inline=False))
            else:
                if answers[int(msg.content) - 1] != correct:
                    embed = dict(color=Color.red(), \
fields=dict(name="Incorrect !", value="The right answer was {}".format(correct), inline=False))
                else:
                    embed = dict(color=Color.green(), title="Correct !")
            message = create_embed(embed)
            await ctx.channel.send(embed=message)

    @commands.command(name="rps")
    @commands.guild_only()
    async def rock_paper_scissor(self, ctx, *, hand):
        """Play Rock, Paper, Scissor"""
        wins = [("rock", "scissor"), ("scissor", "paper"), ("paper", "rock")]
        choices = ["rock", "paper", "scissor"]
        if hand not in choices:
            await ctx.channel.send("{} Do not try to trick me !".format(ctx.author.mention))
        else:
            bot_hand = choice(choices)
            if hand == bot_hand:
                sentence = "It's a draw !"
            elif (hand, bot_hand) in wins:
                sentence = "You have win !"
            else:
                sentence = "I've win !"
            await ctx.channel.send("{} - {} vs {} ! {}".format(\
ctx.author.mention, hand.capitalize(), bot_hand.capitalize(), sentence))


def setup(bot):
    """Add commands to the Bot"""
    bot.add_cog(Games(bot))
