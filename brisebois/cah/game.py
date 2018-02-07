#!/usr/bin/env python

"""Card Against Humanity's game class"""

from asyncio import sleep
from random import sample, shuffle
from discord import CategoryChannel, Guild, TextChannel

from utils.embed import create_embed
from utils.mongodoc import MongoDocument
from .player import Player
from .cards import BlackCard


class Game(MongoDocument):
    """Data class for Game Mongo document"""

    _DATABASE = "cards_against_humanity"
    _COLLECTION = "games"

    # Init
    # ---------------------------------------------------------------------------------------------
    def __init__(self, discord_bot, mongo_client, mongo_session, guild=None):
        super(Game, self).__init__(mongo_client, mongo_session)
        self._bot = discord_bot
        self._set_default_values()
        if guild:
            self._get(guild.id)

    # Properties
    # ---------------------------------------------------------------------------------------------
    @property
    def guild(self):
        """Get Guild

        Returns:
            Guild -- Game's guild
        """
        try:
            return self._bot.get_guild(self._document["guild"])
        except KeyError:
            return None

    @guild.setter
    def guild(self, value):
        """Set guild

        Arguments:
            value {Guild} -- Game's guild

        Raises:
            TypeError -- Wrong type
        """

        if not isinstance(value, Guild):
            raise TypeError("Wrong type for value : %s" % type(value))
        self._document["guild"] = value.id

    @property
    def category(self):
        """Get Category channel

        Returns:
            CategoryChannel -- Game's category channel
        """
        try:
            return self.guild.get_channel(self._document["category"])
        except (AttributeError, KeyError):
            return None

    @category.setter
    def category(self, value):
        """Set Category channel

        Arguments:
            value {CategoryChannel} -- Game's category channel

        Raises:
            TypeError -- Wrong type
        """
        if not isinstance(value, CategoryChannel):
            raise TypeError("Wrong type for value : %s" % type(value))
        self._document["category"] = value.id

    @property
    def board(self):
        """Get Board channel

        Returns:
            TextChannel -- Game's board channel
        """
        try:
            return self.guild.get_channel(self._document["board"])
        except (AttributeError, KeyError):
            return None

    @board.setter
    def board(self, value):
        """Set Board channel

        Arguments:
            value {TextChannel} -- Game's board channel

        Raises:
            TypeError -- Wrong type
        """
        if not isinstance(value, TextChannel):
            raise TypeError("Wrong type for value : %s" % type(value))
        self._document["board"] = value.id

    @property
    def points(self):
        """Get max number of points

        Returns:
            int -- Max number of points
        """
        try:
            return self._document["score"]
        except KeyError:
            return None

    @points.setter
    def points(self, value):
        """Set max number of points

        Arguments:
            value {int} -- Max number of points

        Raises:
            TypeError -- Wrong type
        """
        if not isinstance(value, int):
            raise TypeError("Wrong type for value : %s" % type(value))
        self._document["points"] = value

    @property
    def players_id(self):
        """Get the player's ObjectId

        Returns:
            *ObjectId -- List of ObjectId
        """
        try:
            return self._document["players"]
        except KeyError:
            return None

    @property
    def players(self):
        """Get the players

        Returns:
            *Player -- List of Players
        """
        try:
            return [Player(self._bot, self._client, self._session, _id) for _id in self.players_id]
        except KeyError:
            return None

    @property
    def playing(self):
        """Get the game's status

        Returns:
            bool -- Game's status
        """
        try:
            return self._document["playing"]
        except KeyError:
            return None

    @playing.setter
    def playing(self, value):
        """Set the game status

        Arguments:
            value {bool} -- Game's playing

        Raises:
            TypeError -- Wrong type
        """
        if not isinstance(value, bool):
            raise TypeError("Wrong type for value : %s" % type(value))
        self._document["playing"] = value

    @property
    def voting(self):
        """Get the game's voting status

        Returns:
            bool -- Game's voting status
        """
        try:
            return self._document["voting"]
        except KeyError:
            return None

    @voting.setter
    def voting(self, value):
        """Set the game's voting status

        Arguments:
            value {bool} -- Game's voting status

        Raises:
            TypeError -- Wrong type
        """
        if not isinstance(value, bool):
            raise TypeError("Wrong type for value : %s" % type(value))
        self._document["voting"] = value

    @property
    def black_card(self):
        """Get the last black card drawed

        Returns:
            BlackCard -- Last Black Card drawed
        """
        try:
            return BlackCard(self._client, self._session, self._document["black_cards"][-1])
        except KeyError:
            return None

    @property
    def black_cards(self):
        """Get the Black Cards drawed

        Returns:
            *BlackCard -- List of Black Card drawed
        """
        try:
            return [BlackCard(self._client, self._session, _id) \
                    for _id in self._document["black_cards"]]
        except KeyError:
            return None

    @property
    def white_cards(self):
        """Get the White Cards ObjectId

        Returns:
            *ObjectId -- List of White Cards ObjectId
        """
        try:
            return self._document["white_cards"]
        except KeyError:
            return None

    @property
    def tsar(self):
        """Get the tsar of game

        Returns:
            Player -- Player's Tsar
        """
        try:
            return Player(self._bot, self._client, self._session, self._document["tsar"])
        except KeyError:
            return None

    # Private methods
    # ---------------------------------------------------------------------------------------------
    def _get(self, guild):
        """Get the Mongo document by searching the guild

        Arguments:
            guild {int} -- Guild ID
        """
        document = self._collection.find_one(dict(guild=guild))
        if document:
            self._document = document

    def _set_default_values(self):
        """Set default values for a new document"""
        self._document["guild"] = int()
        self._document["category"] = int()
        self._document["board"] = int()
        self._document["players"] = list()
        self._document["black_cards"] = list()
        self._document["white_cards"] = list()
        self._document["points"] = 15
        self._document["playing"] = False
        self._document["voting"] = False
        self._document["results"] = list()
        self._document["tsar"] = int()

    # Public methods
    # ---------------------------------------------------------------------------------------------
    def add_player(self, player):
        """Add a player to the list of players

        Arguments:
            player {Player} -- Player to delete
        """
        self._document["players"].append(player.document_id)

    def delete_player(self, player):
        """Deletes a player to the list of players

        Arguments:
            player {Player} -- Player to delete
        """
        self._document["players"].remove(player.document_id)

    def set_random_tsar(self):
        """Set the tsar in the beginning of the game"""
        self._document["tsar"] = sample(self.players_id, 1)

    async def score(self):
        """Displays the score on the board"""
        fields = list()
        for player in self.players:
            fields.append(dict(name=player.user.display_name, value=player.score, inline=True))
        message = create_embed(dict(title="Cards Against Humanity", fields=fields))
        await self.board.send(embed=message)

    async def draw_black_card(self):
        """Draw a new black card"""
        query = [{"$sample": {"size": 1}}]
        card_number = len(self._document["black_cards"])
        while len(self._document["black_cards"]) is card_number:
            results = self._client[self._DATABASE]["black_cards"].aggregate(query)
            for document in results:
                if document["_id"] not in self._document["black_cards"]:
                    self._document["black_cards"].append(document["_id"])
        self.save()

    async def send_black_card(self):
        """Send black card to the board"""
        message = create_embed(dict(title="Question - Pick {}".format(self.black_card.pick),
                                    description=self.black_card.text))
        await self.board.send(embed=message)

    async def wait_for_players_answers(self):
        """Waiting for all players to vote before going after"""
        self.voting = True
        self.save()

        # Send message to board
        message = create_embed(dict(title="Time to vote !", \
description="Vote in your private channel by using `{}cah vote`".format(self._bot.command_prefix)))
        await self.board.send(embed=message)

        # Wait players to answers
        number_of_answers = len([p for p in self.players if p.answers])
        while number_of_answers is not len(self.players):
            await sleep(5)
            number_of_answers = len([p for p in self.players if p.answers])

        self.voting = False
        self.save()

    def create_answers(self):
        """Create proposals with players answers"""
        results = list()
        for player in self.players:
            answers = list()
            for answer in player.answers:
                self._document["white_cards"].append(answer.document_id)
                answers.append(answer.text)
            result = self.black_card.text.format(*answers)
            player.clear_answers()
            results.append([player.document_id, result])

        shuffle(results)
        self._document["results"] = results
        self.save()

    async def send_answers(self):
        """Send answers to the board"""
        fields = list()
        for index, value in enumerate(self._document["results"]):
            fields.append(dict(name=index + 1, value=value[1], inline=False))
        embed = create_embed(dict(title="Proposals", fields=fields))
        await self.board.send(embed=embed)

    async def wait_for_tsar_vote(self):
        """Wait for tsar to cast his vote

        Returns:
            str -- Tsar's choice
        """
        def _is_answser(msg):
            return msg.content.isdigit() and msg.author == self.tsar.user and \
                msg.channel == self.tsar.channel

        await self.tsar.channel.send("Vote by typing the number in your channel")
        message = await self._bot.wait_for("message", check=_is_answer)
        return int(message.content)

    async def choose_winner(self, choice):
        """Choose the winner and change tsar

        Arguments:
            choice {int} -- Tsar's choice
        """
        player_id = self._document[choice][0]
        player = Player(self._bot, self._client, self._session, document_id=player_id)
        player.score += 1
        player.save()
        self._document["tsar"] = player_id
        self.save()
        await self.board.send("{} have won this round !".format(player.user.mention))
