#!/bin/env python

"""Games Commands module"""

from asyncio import sleep, TimeoutError
from logging import info
from random import randint

from utils.embed import create_embed

from discord import Color, PermissionOverwrite
from discord.ext import commands
from html2text import html2text


class Cards_Against_Humanity(object):
    """Implements Games commands"""

    def __init__(self, bot):
        self.bot = bot
        self._cah_cards = self.bot.mongo.brisebois.cah_cards
        self._cah_games = self.bot.mongo.brisebois.cah_games

    # Cards Against Humanity - Commands
    # -------------------------------------------------------------------------
    @commands.group(aliases=["cah"])
    async def cardsagainsthumanity(self, ctx):
        """Cards against Humanity game"""
        if ctx.invoked_subcommand is None:
            await ctx.channel.send("No subcommand specified\nUse `{}help {}` to see the list of commands.".format(ctx.prefix, ctx.command))
            await ctx.message.delete()

    @cardsagainsthumanity.command(name="create")
    async def cah_create(self, ctx):
        """Create a new game of Cards Against Humainty"""
        if self._cah_mongo_count_games(ctx.guild.id) is 1:
            content = dict(color=Color.dark_red(), title="Error", description="The number of concurrents games of Cards Against is reached.")
            message = create_embed(**content)
            await ctx.channel.send(embed=message)
        else:
            users = [ctx.author.id]
            for user in ctx.message.mentions:
                if not user.bot and user.id != ctx.author.id:
                    users.append(user.id)
            number = self._cah_mongo_count_games(ctx.guild.id) + 1
            category = await ctx.guild.create_category("CAH - Game #{}".format(number))  # Create Category
            board = await self._cah_channel_create(ctx.guild, category, "board", *users)  # Create Board channel
            channels, score, user_cards = dict(), dict(), dict()
            for user in users:
                channel_name = self._cah_channel_create_name(user)
                channel = await self._cah_channel_create(ctx.guild, category, channel_name, user)  # Create User Channel
                channels[str(user)] = channel.id
                score[str(user)] = 0
                user_cards[str(user)] = list()
            self._cah_mongo_add_game(ctx.guild, number, category, board, users, channels, score, user_cards, "created")

    @cardsagainsthumanity.command(name="start")
    async def cah_start(self, ctx, number, points):
        """Starts a new game of Cards against Humanity"""
        game = self._cah_mongo_get_game(ctx.guild.id, number)
        if len(game["users"]) >= 1:
            self.bot.loop.create_task(self._cah_run(ctx.guild.id, number, int(points)))

    @cardsagainsthumanity.command(name="stop")
    async def cah_stop(self, ctx, number):
        """Stops a game of Cards Against Humanity"""
        await self._cah_stop(ctx.guild.id, number)

    @cardsagainsthumanity.command(name="score")
    async def cah_score(self, ctx, number):
        """Displays the score of the game"""
        message = self._cah_score(ctx.guild.id, number)
        await ctx.channel.send(embed=message)

    @cardsagainsthumanity.command(name="join")
    async def cah_join(self, ctx, number):
        """Join a game of Cards Against Humanity"""
        game = self._cah_mongo_get_game(ctx.guild.id, number)
        if ctx.author.bot:  # Bots cannot join
            content = dict(color=Color.dark_red(), title="Error", description="You're a bot, you cannot join the game !")
            message = create_embed(**content)
            await ctx.channel.send(embed=message)
        elif ctx.author.id in game["users"]:  # Users can't join a second time
            content = dict(color=Color.dark_red(), title="Error", description="You're already in this game ! You want to cheat at Cards Against Humanity ? :rage:")
            message = create_embed(**content)
            await ctx.channel.send(embed=message)
        elif game["status"] is not "started":  # Users can't join a started game
            content = dict(color=Color.dark_red(), title="Error", description="You cannot join ! The game has already started ...")
            message = create_embed(**content)
            await ctx.channel.send(embed=message)
        else:
            game["users"].append(ctx.author.id)  # Add the new user
            guild = self.bot.get_guild(game["guild"])
            board = guild.get_channel(game["board"])  # Get the Board
            category = guild.get_channel(game["category"])  # Get the category
            await self._cah_channel_update(board, ctx.author) # Update permissions on Board
            channel_name = self._cah_channel_create_name(ctx.author)
            channel = await self._cah_channel_create(guild, category, channel_name, ctx.author)  # Create private channel
            game["mapping"].append([ctx.author.id, channel.id])  # Add mapping
            game["score"].append([ctx.author.id, 0])  # Add score
            game["white_cards"].append([ctx.author.id, list()])
            self._cah_mongo_update_game(game)  # Update game in MongoDB

    # Cards Against Humanity -
    # ------------------------------------------------------------------------- 
    async def _cah_stop(self, guild_id, number):
        game = self._cah_mongo_get_game(guild_id, number)
        guild = guild = self.bot.get_guild(game["guild"])
        for user in game["users"]:
            channel = guild.get_channel(game["channels"][str(user)])
            await channel.delete()
        for channel in game["board"], game["category"]:
            channel = guild.get_channel(channel)
            await channel.delete()
        self._cah_mongo_delete_game(game)  # Delete game in Mongo

    def _cah_score(self, guild_id, number):
        game = self._cah_mongo_get_game(guild_id, number)
        content = dict(title="Cards Against Humanity", description="Game #{}".format(game["number"]))
        fields = list()
        for user in game["users"]:
            d_user = self.bot.get_user(user)
            field = dict(name=d_user.display_name, value=game["score"][str(user)], inline=True)
            fields.append(field)
        content["fields"] = fields
        message = create_embed(**content)
        return message

    async def _cah_run(self, guild_id, number, points):
        game = self._cah_mongo_get_game(guild_id, number)
        score_max = 0
        while not score_max is points:
            guild = self.bot.get_guild(game["guild"])
            board = guild.get_channel(game["board"])

            # Send a new black card
            id_black = self._cah_mongo_random_card("black", *game["black_cards"])
            game["black_cards"].append(id_black)
            black = self._cah_mongo_get_card("black", id_black)
            black_message = create_embed(title="Question", description=html2text(black["text"]).replace("_", "\\_"))
            await board.send(embed=black_message)

            # Send White Cards to players
            answers = list()
            for user in game["users"]:
                s_user = str(user)
                channel = guild.get_channel(game["channels"][s_user])
                user_cards = game["user_cards"][s_user]
                while not len(user_cards) is 7:
                    id_white = self._cah_mongo_random_card("white", *game["white_cards"])
                    game["white_cards"].append(id_white)
                    user_cards.append(id_white)
                i, fields = 1, list()
                for id_card in user_cards:
                    white = self._cah_mongo_get_card("white", id_card)
                    field = dict(name=i, value=html2text(white), inline=False)
                    fields.append(field)
                    i += 1
                content = dict(title="Answers", fields=fields)
                white_message = create_embed(**content)
                await channel.send(embed=white_message)
        
            answers = list()
            for user in game["users"]:
                d_user = self.bot.get_user(user)
                await board.send("{} ! Your turn to make a choice. Pick {}".format(d_user.mention, black["pick"]))
                message = await self._cah_wait_user_answer(user, game["channels"][str(user)], guild, black["pick"])
                answers.append(message.content.split())
                for answer in message.content.split():
                    # Pop in reverse order
                    game["user_cards"][s_user].pop(int(answer) - 1)
            score_max += 1
   
    # Channels methods
    def _cah_channel_create_permissions(self, guild, *users):
        permissions = dict()
        permissions[guild.default_role] = PermissionOverwrite(read_messages=False)
        permissions[guild.me] = PermissionOverwrite(read_messages=True, send_messages=True)  # For the bot
        for user in users:
            if isinstance(user, int):
                user = self.bot.get_user(user)
            permissions[user] = PermissionOverwrite(read_messages=True, send_messages=True)
        return permissions

    def _cah_channel_create_name(self, user):
        if isinstance(user, int):
            user = self.bot.get_user(user)
        return "_".join(user.display_name.split())

    async def _cah_channel_create(self, guild, category, name, *users):
        """Create channel with specific permissions"""            
        permissions = self._cah_channel_create_permissions(guild, *users)
        channel = await guild.create_text_channel(name, category=category, overwrites=permissions)
        return channel

    async def _cah_channel_update(self, channel, user):
        """Update channel to add permissions"""
        permissions = PermissionOverwrite(read_messages=True, send_messages=True)
        await channel.set_permissions(user, overwrite=permissions)

    # Mongo methods
    def _cah_mongo_get_game(self, guild, number):
        search = dict(guild=guild, number=int(number))
        return self._cah_games.find_one(search)

    def _cah_mongo_count_games(self, guild):
        search = dict(guild=guild)
        return self._cah_games.find(search).count()

    def _cah_mongo_add_game(self, guild, number, category, board, users, channels, score, user_cards, status):
        document = dict(guild=guild.id, number=number, category=category.id, board=board.id, users=users, channels=channels, score=score, white_cards=list(), black_cards=list(), user_cards=user_cards, status=status)
        self._cah_games.insert_one(document)

    def _cah_mongo_update_game(self, game):
        _id = game.pop("_id")
        self._cah_games.replace_one(dict(_id=_id), game)

    def _cah_mongo_delete_game(self, game):
        _id = game.pop("_id")
        self._cah_games.remove(dict(_id=_id))

    # Mongo Methods - Cards
    def _cah_mongo_random_card(self, color, *cards_played):
        if not color in ["black", "white"]:
            raise ValueError("Color is not black or white")
        cards = self._cah_cards.find_one()
        color_cards = cards[color + "Cards"]
        id_card = randint(0, len(color_cards) - 1)
        while id_card in cards_played:
            id_card = randint(0, len(color_cards) - 1)
        return id_card

    def _cah_mongo_get_card(self, color, id_card):
        if not color in ["black", "white"]:
            raise ValueError("Color is not black or white")
        cards = self._cah_cards.find_one()
        color_cards = cards[color + "Cards"]
        return color_cards[id_card]
    
    async def _cah_wait_user_answer(self, user, channel, guild, pick):
        
        def _is_answer(msg):
            answers, is_all_digit = 0, True
            for answer in msg.content.split():
                if not answer.isdigit():
                    is_all_digit = False
                else:
                    answer += 1
            return is_all_digit and answer == pick and msg.author.id == user and msg.channel.id == channel

        try:
            message = await self.bot.wait_for("message", check=_is_answer, timeout=20.0)
            return message
        except TimeoutError:
            d_channel = guild.get_channel(channel)
            content = dict(color=Color.red(), fields=[dict(name="Sorry !", value="You took too long to answer !", inline=False)])
            error_message = create_embed(**content)
            await d_channel.send(embed=error_message)

def setup(bot):
    """Add commands to the Bot"""
    bot.add_cog(Cards_Against_Humanity(bot))
