#!/bin/env python

"""Discord Bot With Mongo Capabilities"""

from discord.ext.commands import bot
from pymongo import MongoClient

class BotMongo(bot.Bot):
    """Extends the standard bot with Mongo capabilities"""

    #pylint: disable-msg=too-many-arguments
    def __init__(self, command_prefix, formatter=None, description=None,
                 pm_help=False, mongo_host="localhost", mongo_port=27017,
                 **options):
        super(BotMongo, self).__init__(command_prefix, formatter, description,
                                       pm_help, **options)
        self.mongo = MongoClient(host=mongo_host, port=mongo_port,
                                 connect=False)

    def get_api_key(self, key):
        """Get the specified API key

        Arguments:
            key {str} -- Name of the key
        """
        database = self.mongo.brisebois.api_keys
        entry = database.find_one({key: {"$exists": True}})
        return entry[key]
