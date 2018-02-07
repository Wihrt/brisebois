#!/usr/bin/env python

"""Check functions"""

from discord import DMChannel
from discord.ext import commands


def private_only(ctx):
    """Checks if the channel is a DMChannel

    Arguments:
        ctx {Context} -- Context of the message

    Returns:
        bool -- Result of check
    """
    return isinstance(ctx.channel, DMChannel)
