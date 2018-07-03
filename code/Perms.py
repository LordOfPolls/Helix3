devs = ["174918559539920897","269543926803726336","245994206965792780","248790930541248512","142013432403722241"] 
staff = []      #staff id and dev id should be in their own lines or on_member_join will break
donators = []

class Perms:
    @staticmethod
    def donatorOnly(ctx):
        if message.ctx.author.id not in []:
            return staffOnly(ctx)  # staff override
        else:
            return True

    @staticmethod
    def devOnly(ctx):
        return ctx.message.author.id in devs

    @staticmethod
    def staffOnly(ctx):
        return ctx.message.author.id in staff or ctx.message.author.id in devs

    @staticmethod
    def adminOnly(ctx):
        if Perms.staffOnly(ctx):
            return True
        perms = ctx.message.author.permissions_in(ctx.message.channel)
        return perms.administrator

    @staticmethod
    def kickOnly(ctx):
        perms = ctx.message.author.permissions_in(ctx.message.channel)
        return perms.kick_members

    @staticmethod
    def banOnly(ctx):
        perms = ctx.message.author.permissions_in(ctx.message.channel)
        return perms.ban_members

    @staticmethod
    def manageMessagesOnly(ctx):
        perms = ctx.message.author.permissions_in(ctx.message.channel)
        return perms.manage_messages

    @staticmethod
    def manageServerOnly(ctx):
        perms = ctx.message.author.permissions_in(ctx.message.channel)
        return perms.manage_server