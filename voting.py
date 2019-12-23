from discord.ext import tasks, commands
import asyncio
from datetime import datetime
from datetime import timedelta
import discord
import json


class Proposition():
    embedMessage = discord.Embed()
    title, author, starttime = "" , "" , None
    color = 0x0055ff

    ayes, nays = [], []
    status = "Voting..."

    def __init__(self, title, author, starttime):
        self.title = title
        self.author = author
        self.starttime = starttime

        self.ayes, self.nays = [], []

    def getEmbed(self):
        self.embedMessage = discord.Embed()

        self.embedMessage.title = self.title
        self.embedMessage.color = self.color
        self.embedMessage.add_field(name="Author", value=self.author, inline=True)

        strStartTime = self.starttime.strftime("%H:%M:%S")
        strEndTime = (self.starttime + timedelta(hours=1)).strftime("%H:%M:%S")
        self.embedMessage.add_field(name="Time", value=strStartTime, inline=True)
        self.embedMessage.add_field(name="End Time", value=strEndTime, inline=True)

        ayeText, nayText = "\n".join(self.ayes), "\n".join(self.nays)
        if(ayeText == ""):
            ayeText = "No voters yet!"
        if(nayText == ""):
            nayText = "No voters yet!"

        self.embedMessage.add_field(name="Ayes", value=ayeText, inline=False)
        self.embedMessage.add_field(name="Nays", value=nayText, inline=False)

        self.embedMessage.set_footer(text="Status: {}".format(self.status))
        return self.embedMessage

class Voting(commands.Cog):

    vote_in_progress = False
    currentProp = None

    dm_messages = []
    start_message = None

    @tasks.loop(seconds=1)
    async def check_expire(self):
        if(self.vote_in_progress == False):
            return
        await self.checkVotingOver()

    def __init__(self, bot):
        self.bot = bot
        self.check_expire.start()

    async def sendVoteDM(self, ctx):

        self.dm_messages = []
        for member in ctx.channel.members:
            if(member.bot):
                continue

            try:
                if(member.dm_channel == None):
                    await member.create_dm()
                msg = await member.dm_channel.send(embed=self.currentProp.getEmbed())
                self.dm_messages.append(msg)
                await msg.add_reaction("👍")
                await msg.add_reaction("👎")
            except discord.Forbidden:
                print("Could not send message to user {}".format(member))

    async def updateMessages(self):
        for dmmsg in self.dm_messages:
            await dmmsg.edit(embed=self.currentProp.getEmbed())
        await self.start_message.edit(embed=self.currentProp.getEmbed())

    async def checkVotingOver(self):

        votingMem = []
        for m in self.start_message.channel.members:
            if(m.bot):
                continue
            votingMem.append(m)

        if(len(self.currentProp.ayes) + len(self.currentProp.nays) == len(votingMem) or\
           self.currentProp.starttime + timedelta(hours=1) < datetime.now()):

            if(len(self.currentProp.ayes) < len(self.currentProp.nays)):
                self.currentProp.status = "Rejected."
                self.currentProp.color = 0xff3311
            elif(len(self.currentProp.ayes) > len(self.currentProp.nays)):
                #TODO: Allow Derek Veto?

                self.currentProp.status = "Passed."
                self.currentProp.color = 0x00ff11
            else:
                # derek vote tiebreak
                if("Airikan#7238" in self.currentProp.ayes):
                #TODO: Allow Derek Veto?
                    self.currentProp.status = "Passed. (with tiebreak)"
                    self.currentProp.color = 0x00ff11
                elif("Airikan#7238" in self.currentProp.nays):
                    self.currentProp.status = "Rejected. (with tiebreak)"
                    self.currentProp.color = 0xff3311
                else:
                    self.currentProp.status = "Failed to Reach Decision."
                    self.currentProp.color = 0xffe605
            self.vote_in_progress = False
            await self.updateMessages()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if(user.bot):
            return
        for m in self.dm_messages:
            if(m.id == reaction.message.id):
                break
        else:
            return
        if(str(user) in self.currentProp.ayes or str(user) in self.currentProp.nays):
            await reaction.message.channel.send("You've already voted!")
            return

        if(reaction.emoji == "👍"):
            await reaction.message.channel.send("Aye (👍) vote registered.")
            self.currentProp.ayes.append(str(user))
        elif(reaction.emoji == "👎"):
            await reaction.message.channel.send("Nay (👎) vote registered.")
            self.currentProp.nays.append(str(user))

        await self.updateMessages()
        await self.checkVotingOver()


    @commands.command()
    async def startvote(self, ctx, *args):
        if(self.vote_in_progress):
            retStr = str("""```css\nProposition already in progress```""")
            await ctx.send(retStr)
            return

        self.vote_in_progress = True
        print("{0.author}\t has started a vote to\t {1}!".format(ctx, " ".join(args)))

        self.currentProp = Proposition(" ".join(args), ctx.author, datetime.now())
        self.start_message = await ctx.send(embed=self.currentProp.getEmbed())

        print("Sending options to moderator/admin")
        await self.sendVoteDM(ctx)
        await self.checkVotingOver()

def setup(bot):
   bot.add_cog(Voting(bot))

