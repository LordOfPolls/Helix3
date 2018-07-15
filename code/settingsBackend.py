import discord
import json
import os

class Settings:
    class Get:
        @staticmethod
        def _loadJson(server):
            dir = "data/{}".format(server.id)
            if not os.path.exists(dir):
                os.mkdir(dir)
            dir += "/settings.json"
            if not os.path.isfile(dir):
                return None
            r =open(dir, 'r')
            data = json.load(r)
            r.close()
            return data

        def announcementChannel(self, server):
            try:
                data = self._loadJson(server)
                if data is not None:
                    channel = str(data['announcement'])
                    channel = discord.Object(channel)
                    return channel
                return None
            except:
                return None

        def prefix(self, server):
            try:
                data = self._loadJson(server)
                if data is not None:
                    prefix = str(data['prefix'])
                    return prefix
                return "."
            except:
                return "."

        def welcomeChannel(self, server):
            try:
                data = self._loadJson(server)
                if data is not None:
                    welcomeChannel = str(data['welcome'])
                    welcomeChannel = discord.Object(welcomeChannel)
                    return welcomeChannel
                return None
            except:
                return None

        def blacklist(self, server):
            try:
                data = self._loadJson(server)
                if data is not None:
                    blacklist = list(data['blacklist'])
                    return blacklist
                return None
            except:
                return None

        def modlogChannel(self, server):
            try:
                data = self._loadJson(server)
                if data is not None:
                    modlog = str(data['modlog'])
                    modlog = discord.Object(modlog)
                    return modlog
                return None
            except:
                return None

    class Set:
        @staticmethod
        def _setupJson(server, prefix=".", announcement=None, welcome=None, blacklist=None, modlog=None):
            template = {"prefix": prefix, "announcement": announcement,
                        "welcome": welcome, "blacklist": blacklist,
                        "modlog": modlog}

            dir = "data/{}".format(server.id)
            if not os.path.exists(dir):
                os.mkdir(dir)
            dir += "/settings.json"
            file = open(dir, 'w')
            json.dump(template, file)
            file.close()

        def _loadJson(self, server):
            dir = "data/{}".format(server.id)
            if not os.path.exists(dir):
                os.mkdir(dir)
            dir += "/settings.json"
            if not os.path.isfile(dir):
                self._setupJson(server)
            r = open(dir, 'r')
            data = json.load(r)
            r.close()
            return data

        def _resetJson(self, server):
            dir = "data/{}/settings.json".format(server.id)
            os.unlink(dir)
            self._setupJson(server)

        def new(self, server, prefix=None, announcement=None, welcome=None, blacklist=None, modlog=None):
            data = self._loadJson(server)
            if prefix != None:
                data['prefix'] = prefix
            if announcement is not None:
                data['announcement'] = announcement
            if welcome is not None:
                data['welcome'] = welcome
            if blacklist is not None:
                data['blacklist'] = blacklist
            if modlog is not None:
                data['modlog'] = modlog
            r = open("data/{}/settings.json".format(server.id), "w")
            r.seek(0)
            r.write(json.dumps(data))
            r.truncate()
            r.close()







