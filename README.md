# Helix3
The third iteration of Helix

Oh hey, this bot is a work in progress. If you want to help out, go ahead.

## So what does each file do?

``boot.py`` prepares the bot to boot, handles the logging setup and archive. You run this file to start the bot

``code/bot.py``the main bot file. This code handles loading and unloading cogs, logging in, shutting down, and all other core functions

``code/fun.py`` a cog file for all "fun" commands

``code/moderation.py`` a cog for all "moderation" commands

``code/music.py`` a cog for all music functions

``code/utilites.py`` a cog for all "utilities" commands

``code/porn.py`` a cog for all the *cough* naughty commands

``code/get.py`` is an unfinnished collection of helper functions to allow per server settings

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

### Extra dependencies
- `youtube_dl`
- `colorlog`
- `lxml`
- `discord`

### For anything else, use the following:
standard discord.py stuff: http://discordpy.readthedocs.io/en/latest/

commands extension stuff (cogs, commands.command, etc.): http://discordpy.readthedocs.io/en/latest/faq.html#commands-extension

https://www.google.co.uk
