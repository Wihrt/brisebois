#!/bin/env python
from discord import Embed
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from lib.utils import get_key
from requests import get


class Weather(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,
                      help="Give weathers informations for maps")
    @commands.cooldown(60, "60.0", BucketType.default)
    async def weather(self, ctx, *city):
        key = get_key(self.bot.API_KEYS, "weather")
        payload = dict(q=" ".join(city), APPID=key, units="metric")
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
            value="{} km/h".format(json["wind"]["speed"]))
        await self.bot.send_message(ctx.message.channel, embed=message)
        return


def setup(bot):
    bot.add_cog(Weather(bot))
