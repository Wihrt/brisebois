#!/bin/env python

"""Weather Commands module"""

from utils.embed import create_embed

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from requests import get


class Misc(object):  # pylint: disable=too-few-public-methods
    """Implements Misc commands"""

    def __init__(self, bot):
        self.bot = bot
        self._weather_api_key = self.bot.get_api_key("weather")

    @commands.command()
    @commands.cooldown(60, "60.0", BucketType.default)
    async def weather(self, ctx, *search):
        """Give weathers informations on cities"""
        content = self._weather("http://api.openweathermap.org/data/2.5/weather", self._weather_api_key, search)
        message = create_embed(**content)
        await ctx.channel.send(embed=message)

    @staticmethod
    def _weather(url, api_key, search):
        payload = dict(q=" ".join(search), APPID=api_key, units="metric")
        response = get(url, params=payload)
        response.raise_for_status()
        json = response.json()
        weather = dict(name=":partly_sunny", value=json["weather"][0]["description"].capitalize(), inline=True)
        temperature = dict(name=":thermometer", value="{} °C".format(json["main"]["temp"]))
        humidity = dict(name=":droplet:", value="{} %".format(json["main"]["humidity"]))
        wind = dict(name=":dash:", value="{} m/s".format(json["wind"]["speed"]))
        content = dict(title="Weather of {0}, {1}".format(json["name"], json["sys"]["country"]),
                       thumbnail="https://openweathermap.org/img/w/{}.png".format(json["weather"][0]["icon"]),
                       fields=[weather, temperature, humidity, wind])
        return content


def setup(bot):
    """Add commands to the bot"""
    bot.add_cog(Misc(bot))
