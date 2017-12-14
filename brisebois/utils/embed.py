#!/bin/env python

"""Utilities classes and functions"""

from discord import Embed


def create_embed(author=None, color=None, description=None, fields=None, footer=None, title=None, thumbnail=None, url=None):
    """Wrapper to create Embed message with all parameters sets"""
    message = Embed()
    if isinstance(author, dict):
        message.set_author(**author)
    if color:
        message.colour = color
    if description:
        message.description = description
    if isinstance(fields, list):
        for field in fields:
            if isinstance(field, dict):
                message.add_field(**field)
    if isinstance(footer, dict):
        message.set_footer(**footer)
    if title:
        message.title = title
    if thumbnail:
        message.set_thumbnail(url=thumbnail)
    if url:
        message.set_image(url=url)
    return message
