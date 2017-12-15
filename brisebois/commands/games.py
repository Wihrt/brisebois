#!/bin/env python

"""Games Commands module"""

from asyncio import TimeoutError
from html import unescape
from logging import info
from random import shuffle

from utils.embed import create_embed

from discord import Color, PermissionOverwrite
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from requests import get

class Games(object):
    """Implements Games commands"""

    def __init__(self, bot):
        self.bot = bot
        self._cah_games = self.bot.mongo.brisebois.cah_games

    # Commands
    # -------------------------------------------------------------------------
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

    @commands.group(aliases=["cah"])
    async def cardsagainsthumanity(self, ctx):
        """Cards against Humanity game"""
        if ctx.invoked_subcommand is None:
            await ctx.channel.send("No subcommand specified\nUse `{}help {}` to see the list of commands.".format(ctx.prefix, ctx.command))
            await ctx.message.delete()
        
    @cardsagainsthumanity.command()
    async def start(self, ctx):
        """Starts a new game of Cards against Humanity"""
        
        def _is_answer(m):
            return m.content.isdigit() and m.author == author and m.channel == channel

        # Create category
        name = self._mongo_create_game(self._cah_games, ctx.guild)
        category = await ctx.guild.create_category(name)
        board_permissions = self._create_channel_permissions(ctx.guild, *ctx.message.mentions)
        board = await ctx.guild.create_text_channel("board", category=category, overwrites=board_permissions)

        # Create channel per user
        mapping = list()
        for user in ctx.message.mentions:
            user_permissions = self._create_channel_permissions(ctx.guild, user)
            user_channel = await ctx.guild.create_text_channel("_".join(user.display_name.split()), category=category, overwrites=user_permissions)
            mapping.append([user, user_channel])

        await board.send("Send a number from your channel")
        for author, channel in mapping:
            await board.send('{} have to choose an answer'.format(author.mention))
            message = await self.bot.wait_for("message", check=_is_answer)
            await board.send("Response received from {}".format(author.mention))

    @staticmethod
    def _mongo_create_game(games, guild, pattern="CAH GAME #{}"):
        number = games.find().count()
        name = pattern.format(number + 1)
        document = dict(guild=guild.id, name=name)
        games.insert_one(document)
        return name

    @staticmethod
    def _create_channel_permissions(guild, *users):
        permissions = dict()
        permissions[guild.default_role] = PermissionOverwrite(read_messages=False)
        permissions[guild.me] = PermissionOverwrite(read_messages=True, send_messages=True)  # For the bot
        for user in users:
            permissions[user] = PermissionOverwrite(read_messages=True, send_messages=True)
        return permissions

    # Static methods
    # -------------------------------------------------------------------------
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
