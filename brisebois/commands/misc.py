#!/bin/env python

"""Weather Commands module"""

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from utils.api import ApiKey
from utils.embed import create_embed


class Misc(object):  # pylint: disable=too-few-public-methods
    """Implements Misc commands"""

    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = self.bot.mongo
        self.mongo_session = self.mongo_client.start_session()
        self.weather_key = ApiKey(self.mongo_client, self.mongo_session, "weather").value

    # Commands
    # -------------------------------------------------------------------------
    @commands.command()
    @commands.cooldown(60, "60.0", BucketType.default)
    @commands.guild_only()
    async def weather(self, ctx, *, search):
        """Give weather informations searched city"""
        params = dict(q=search, APPID=self.weather_key, units="metric")
        response = await self.bot.session.get("http://api.openweathermap.org/data/2.5/weather",
                                              params=params)
        async with response:
            content = await response.json()
            title = "Weather of {0}, {1}".format(content["name"], content["sys"]["country"])
            thumbnail = "https://openweathermap.org/img/w/{}.png".format(
                content["weather"][0]["icon"])
            weather = dict(name=":partly_sunny:",
                           value=content["weather"][0]["description"].capitalize(),
                           inline=True)
            temperature = dict(name=":thermometer", value="{} °C".format(content["main"]["temp"]))
            humidity = dict(name=":droplet:", value="{} %".format(content["main"]["humidity"]))
            wind = dict(name=":dash:", value="{} m/s".format(content["wind"]["speed"]))
            embed = dict(title=title, thumbnail=thumbnail,
                         fields=[weather, temperature, humidity, wind])
            message = create_embed(embed)
            await ctx.channel.send(embed=message)


def setup(bot):
    """Add commands to the bot"""
    bot.add_cog(Misc(bot))
