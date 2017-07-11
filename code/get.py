import os
import json
import asyncio
import discord

async def Announce(server):
    dir = "data/" + server.id + ".json"
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.isfile(dir):
        channel = server
    else:
        with open(dir, 'r') as r:
            data = json.load(r)
            channel = str(data["announcement"])
            channel = discord.Object(channel)
    return channel


async def Prefix(server):
    dir = "data/" + server.id + ".json"
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.isfile(dir):
        prefix = self.prefix
    else:
        with open(dir, 'r') as r:
            data = json.load(r)
            prefix = str(data["prefix"])
    return prefix


async def Welcome(server):
    dir = "data/" + server.id + ".json"
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.isfile(dir):
        welcome = None
    else:
        with open(dir, 'r') as r:
            data = json.load(r)
            welcome = discord.Object(data['welcome'])
    return welcome

async def Blacklist(server):
    dir = "data/" + server.id + ".json"
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.isfile(dir):
        blacklist = None
    else:
        with open(dir, 'r') as r:
            data = json.load(r)
            blacklist = list(data['blacklist'])
    return blacklist


async def Modlog(server):
    dir = "data/" + server.id + ".json"
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.isfile(dir):
        modlog = None
    else:
        with open(dir, 'r') as r:
            data = json.load(r)
            modlog = data['modlog']
    return modlog


async def Alias(word):
    if not os.path.isfile("BlacklistAlias/{}.json".format(word)):
        return None
    else:
        f = open("BlacklistAlias/{}.json".format(word), "r")
        data = json.load(f)
        aliases = list(data['Aliases'])
        return aliases

async def Mute(server):
    dir = "data/" + server.id + ".json"
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.isfile(dir):
        muted = None
    else:
        with open(dir, 'r') as r:
            data = json.load(r)
            muted = data['muted']
    return muted