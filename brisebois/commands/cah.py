#!/bin/env python

"""Cards Against Humanity command module"""

from discord import Color
from discord.ext import commands

from cah.game import Game
from cah.player import Player

from utils.embed import create_embed

class CardsAgainstHumanity(object):
    """Implements Cards Against Humanity commands"""

    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = self.bot.mongo
        self.mongo_session = self.mongo_client.start_session()

    # Cards Against Humanity - Commands
    # -------------------------------------------------------------------------
    @commands.group(aliases=["cah"])
    @commands.guild_only()
    async def cardsagainsthumanity(self, ctx):
        """Cards Against Humanity top command"""
        if ctx.invoked_subcommand is None:
            await ctx.channel.send("No subcommand specified\n\
Use `{}help {}` to see the list of commands.".format(ctx.prefix, ctx.command))
            await ctx.message.delete()

    @cardsagainsthumanity.command()
    @commands.guild_only()
    async def create(self, ctx):
        """Create a new game of Cards Against Humanity"""
        game = Game(self.bot, self.mongo_client, self.mongo_session, ctx.guild)
        if game.document_id is not None:
            pass  # Send an error
        else:
            game.guild = ctx.guild
            game.category = await ctx.guild.create_category("Cards Against Humanity")
            game.board = await ctx.guild.create_text_channel("board", category=game.category)
            game.save()
            await ctx.message.delete()

    @cardsagainsthumanity.command()
    @commands.guild_only()
    async def delete(self, ctx):
        """Delete a game of Cards Against Humanity"""
        game = Game(self.bot, self.mongo_client, self.mongo_session, ctx.guild)
        for player in game.players:
            await player.channel.delete()
            player.delete()
        await game.board.delete()
        await game.category.delete()
        game.delete()
        await ctx.message.delete()

    @cardsagainsthumanity.command()
    @commands.guild_only()
    async def join(self, ctx):
        """Join a Cards Against Humanity game"""
        await ctx.message.delete()
        game = Game(self.bot, self.mongo_client, self.mongo_session, ctx.guild)
        player = Player(self.bot, self.mongo_client, self.mongo_session, user=ctx.author)
        if game.playing:
            await ctx.author.send("The game is already playing, you cannot join")
        elif player.document_id in game.players_id:
            await ctx.author.send("You are already in this game. You wouldn't cheat, right ?")
        else:
            name = "_".join(ctx.author.display_name.split())
            player.guild = ctx.guild
            player.user = ctx.author
            player.channel = await ctx.guild.create_text_channel(name, category=game.category)
            player.save()
            game.add_player(player)
            game.save()
            await game.board.send("{} has joined the game".format(ctx.author.mention))

    @cardsagainsthumanity.command()
    @commands.guild_only()
    async def leave(self, ctx):
        """Leave the game"""
        await ctx.message.delete()
        game = Game(self.bot, self.mongo_client, self.mongo_session, ctx.guild)
        player = Player(self.bot, self.mongo_client, self.mongo_session, user=ctx.author)
        if player.document_id in game.players_id:
            game.delete_player(player)
            if player.document_id == game.tsar.document_id:
                game.set_random_tsar()
            game.save()
            await player.channel.delete()
            player.delete()
            await game.board.send("{} has leaved the game".format(ctx.author.mention))

    @cardsagainsthumanity.command()
    @commands.guild_only()
    async def start(self, ctx, points=15):
        """Starts the game"""
        await ctx.message.delete()
        game = Game(self.bot, self.mongo_client, self.mongo_session, ctx.guild)
        if not len(game.players) > 3:
            await game.board.send("You must be 3 players at least to start the game")
        elif not game.playing:
            game.playing = True
            game.points = points
            game.save()
            self.bot.loop.create_task(self.run(game))

    @cardsagainsthumanity.command()
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops the game"""
        game = Game(self.bot, self.mongo_client, self.mongo_session, ctx.guild)
        game.playing = False
        game.save()

    @cardsagainsthumanity.command()
    @commands.guild_only()
    async def vote(self, ctx, *answers):
        """Give your white cards for the answers"""
        await ctx.message.delete()
        game = Game(self.bot, self.mongo_client, self.mongo_session, ctx.guild)
        if game.playing:
            player = Player(self.bot, self.mongo_client, self.mongo_session, user=ctx.author)
            if player.document_id not in game.players_id:
                await ctx.author.send("You are not a player in this game !")
            elif ctx.channel != player.channel:
                await ctx.author.send("You must send in your dedicated channel")
            elif player.document_id == game.tsar.document_id:
                await player.channel.send("You are the Tsar ! You must wait other player's anwers")
            elif not game.voting:
                await player.channel.send("It's not the time to vote ! You must wait")
            elif game.black_card.pick is not len(answers):
                await ctx.channel.send("You have sent {} answer but \
you must pick {} answers".format(len(answers), game.black_card.pick))
            elif not all(i in range(1, 8) for i in answers):
                await ctx.channel.send("Answers must be between 1 and 7")
            else:
                player.add_answers(list(map(int, answers)))
                await game.board.send("{} has voted !".format(ctx.author.mention))

    @cardsagainsthumanity.command()
    @commands.guild_only()
    async def score(self, ctx):
        """Give the score"""
        game = Game(self.bot, self.mongo_client, self.mongo_session, ctx.guild)
        if not game.document_id:
            message = create_embed(dict(color=Color.dark_red(), title="Error", \
description="No game of Cards Against Humanity is created."))
            await ctx.channel.send(embed=message)
        else:
            game.score()

    async def run(self, game):
        """Run the game"""
        game.set_random_tsar()  # Set the Tsar
        while game.playing and all(p.score < game.points for p in game.players):
            game.draw_black_card()  # Draw a new Black card
            await game.send_black_card()  # Send black card to board
            for player in game.players:
                player.draw_white_cards(game.white_cards)  # Draw white cards for players
                await player.send_white_cards()  # Send white cards to dedicated channel
            await game.wait_for_players_answers()
            await game.send_answers()  # Send all answers to the board
            choice = await game.wait_for_tsar_vote()
            game.choose_winner(choice)
            game.score()
        game.playing = False
        game.save()

def setup(bot):
    """Add commands to the Bot"""
    bot.add_cog(CardsAgainstHumanity(bot))
