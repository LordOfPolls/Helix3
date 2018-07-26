[![](https://travis-ci.com/LordOfPolls/Helix3.svg?branch=Stable)](https://travis-ci.com/LordOfPolls/Helix3) 
![](https://img.shields.io/github/last-commit/LordOfPolls/Helix3.svg) 
![](https://img.shields.io/discord/460074170475085825.svg) 
![](https://img.shields.io/github/commit-activity/y/LordOfPolls/Helix3.svg)
![](https://img.shields.io/badge/Version-Beta-red.svg)
# Helix3
The third iteration of Helix

# How do i install?
Check the wiki, install and config guides are there

## So what does each file do?

``boot.py`` prepares the bot to boot, handles the logging setup and archive. You run this file to start the bot

``code/bot.py``the main bot file. This code handles loading and unloading cogs, logging in, shutting down, and all other core functions

``code/fun.py`` a cog file for all "fun" commands

``code/moderation.py`` a cog for all "moderation" commands

``code/music.py`` a cog for all music functions

``code/utilites.py`` a cog for all "utilities" commands

``code/porn.py`` a cog for all the *cough* naughty commands

``code/get.py`` is an unfinnished collection of helper functions to allow per server settings

``code/chatbot.py`` a cog for helix's chatbot capability, based on A.L.I.C.E. AIML Bot

Any code files prefaced with "misc_" are just files that return a random string in line with 1the name. These will be gone soon so just ignore them.

### How do i load a cog?
```py
bot.add_cog([cogName](param))
```
### How do i unload a cog?
```py
bot.remove_cog("[cogName]")
```
### Can my cog be added to reload?
Yeah, just use the rest of the command as guidance

### Can i use the requests module?
NO, use ``aiohttp.get`` instead

### How do i make a command?
Go to the appropriate cog file, go into the class and use the following:
```py
    @commands.command(pass_context=[bool], no_pm=[bool])
    async def [command name](self, ctx): # use ctx, if pass_context is true
        [code for your command]
 ```

### Dependencies
(this list isnt always up to date, check [requirements.txt](https://raw.githubusercontent.com/LordOfPolls/Helix3/Stable/requirements.txt))
- `discord.py[voice]`
- `colorlog`
- `pycryptodome`
- `requests`
- `imgurpython`
- `lxml`
- `pillow`
- `bs4`
- `youtube_dl`
- `https://github.com/LordOfPolls/Python-AIML-Logging/archive/master.zip`

### For anything else, use the following:
standard discord.py stuff: http://discordpy.readthedocs.io/en/latest/

commands extension stuff (cogs, commands.command, etc.): http://discordpy.readthedocs.io/en/latest/faq.html#commands-extension

https://www.google.co.uk
