import asyncio
import discord
from discord.ext import commands
from xml.etree import cElementTree as ET
from collections import defaultdict
import code.get as get
import aiohttp
import random
import rule34
import logging

import code.Perms as Perms
Perms = Perms.Perms

log = logging.getLogger(__name__)

class Porn:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=False)
    async def rule34(self, ctx):
        """Search rule 34
        Seperate multiple tags with ','"""
        await self.bot.send_typing(ctx.message.channel)
        tags = ctx.message.content.lower().replace("rule34", "")
        tags = tags.replace(".", "")
        tags = tags.replace("<@{}>".format(self.bot.user.id), "") # mention
        tags = tags.replace("<@!{}>".format(self.bot.user.id), "") # mention w/ nickname
        tags = tags.strip()
        if tags == "":
            await self.bot.send_message(ctx.message.channel, "Please search for something\nUse ``,`` to seperate search terms")
            return
        else:
            tags = tags.replace(", ", ",").replace(" ", "_")
            tags = tags.replace(",", " ")  # ignore this
            imgList = await Rule34(self.bot)._getImageURLS(tags=tags)

            if imgList != None:
                em = discord.Embed(color=16738740)
                em.set_image(url=random.choice(imgList))
            else:
                em = discord.Embed(description="No results", color=16711680)
            await self.bot.send_message(ctx.message.channel, embed=em)





class Rule34:
    """Based on my rule34 api, modified for async"""
    def __init__(self, bot):
        self.session = aiohttp.ClientSession(loop=bot.loop)

    @staticmethod
    def _urlGen(tags=None, limit=None, id=None, PID=None, deleted=None, **kwargs):
        """Generates a URL to access the api using your input:
        Arguments:
            "limit"  ||str ||How many posts you want to retrieve
            "pid"    ||int ||The page number.
            "tags"   ||str ||The tags to search for. Any tag combination that works on the web site will work here. This includes all the meta-tags. See cheatsheet for more information.
            "cid"    ||str ||Change ID of the post. This is in Unix time so there are likely others with the same value if updated at the same time.
            "id"     ||int ||The post id.
            "deleted"||bool||If True, deleted posts will be included in the data
        All arguments that accept strings *can* accept int, but strings are recommended
        If none of these arguments are passed, None will be returned
        """
        # I have no intentions of adding "&last_id=" simply because its response can easily be massive, and all it returns is ``<post deleted="[ID]" md5="[String]"/>`` which has no use as far as im aware
        URL = "https://rule34.xxx/index.php?page=dapi&s=post&q=index"
        if PID != None:
            URL += "&pid={}".format(PID)
        if limit != None:
            URL += "&limit={}".format(limit)
        if id != None:
            URL += "&id={}".format(id)
        if tags != None:
            tags = str(tags).replace(" ", "+")
            URL += "&tags={}".format(tags)
        if deleted == True:
            URL += "&deleted=show"
        if PID != None or limit != None or id != None or tags != None:
            return URL
        else:
            return None

    async def _totalImages(self, tags):
        """Get an int of how many images are on rule34.xxx
        Argument: tags (string)"""
        XML = None
        with aiohttp.Timeout(10):
            async with self.session.get(self._urlGen(tags=tags, PID=0)) as XMLData:
                XMLData = await XMLData.read()
                XMLData = ET.XML(XMLData)
                XML = self.ParseXML(XMLData)
        return int(XML['posts']['@count'])

    async def _getImageURLS(self, tags):
        """Returns a list of all images/webms/gifs it can find
        This function can take a LONG time to finish with huge tags. E.G. in my testing "gay" took 200seconds to finish (740 pages)
        Argument: tags (string)"""
        if await self._totalImages(tags) != 0:
            imgList = []
            if tags == "random":
                tempURL = self._urlGen(PID=random.randint(0, 1000))

            else:
                tempURL = self._urlGen(tags=tags)
            with aiohttp.Timeout(10):
                async with self.session.get(tempURL) as XML:
                    XML = await XML.read()
                    XML = self.ParseXML(ET.XML(XML))
                    for data in XML['posts']['post']:
                        imgList.append(str(data['@file_url']))
            await self.session.close()
            return imgList
        else:
            await self.session.close()
            return None
    
    def ParseXML(self, rawXML):
        """Parses entities as well as attributes following this XML-to-JSON "specification"
        Using https://stackoverflow.com/a/10077069"""
        if "Search error: API limited due to abuse" in str(rawXML.items()):
            raise Rule34_Error('Rule34 rejected your request due to "API abuse"')

        d = {rawXML.tag: {} if rawXML.attrib else None}
        children = list(rawXML)
        if children:
            dd = defaultdict(list)
            for dc in map(self.ParseXML, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {rawXML.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if rawXML.attrib:
            d[rawXML.tag].update(('@' + k, v) for k, v in rawXML.attrib.items())
        if rawXML.text:
            text = rawXML.text.strip()
            if children or rawXML.attrib:
                if text:
                    d[rawXML.tag]['#text'] = text
            else:
                d[rawXML.tag] = text
        return d
