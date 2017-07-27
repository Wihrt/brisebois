#!/bin/env python

"""Weather Commands module"""


from discord import Embed
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from requests import get
from pymongo import MongoClient


class Weather(object):  # pylint: disable=too-few-public-methods
    """Implements Weather commands"""

    def __init__(self, bot):
        self.bot = bot
        self.key = self._get_api_key()

    @commands.command(pass_context=True)
    @commands.cooldown(60, "60.0", BucketType.default)
    async def weather(self, ctx, *args) -> None:
        """Give weathers informations on cities

        Args:
            ctx: Context of the message
            args (str): Cities to get weather

        Returns: None
        """
        payload = dict(q=" ".join(args), APPID=self.key, units="metric")
        json = get("http://api.openweathermap.org/data/2.5/weather",
                   params=payload).json()
        message = Embed(
            title="Weather of {0}, {1}".format(
                json["name"], json["sys"]["country"]))
        message.set_thumbnail(
            url="https://openweathermap.org/img/w/{}.png".format(
                json["weather"][0]["icon"]))
        message.add_field(
            name=":partly_sunny:",
            value=json["weather"][0]["description"].capitalize())
        message.add_field(
            name=":thermometer:",
            value="{} °C".format(json["main"]["temp"]))
        message.add_field(
            name=":droplet:",
            value="{} %".format(json["main"]["humidity"]))
        message.add_field(
            name=":dash:",
            value="{} m/s".format(json["wind"]["speed"]))
        await self.bot.send_message(ctx.message.channel, embed=message)

    # MongoDB methods
    @staticmethod
    def _get_api_key() -> None:
        client = MongoClient()
        database = client.brisebois.api_keys
        entry = database.find_one({"weather": {"$exists": True}})
        return entry["weather"]


def setup(bot):
    """Add commands to the bot.

    Args:
        bot: Bot which will add the commands

    Returns:
        None
    """
    bot.add_cog(Weather(bot))
