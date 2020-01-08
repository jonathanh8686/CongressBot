from discord.ext import tasks, commands
import pytz
import asyncio
from datetime import datetime
from datetime import timedelta
import discord
import json

class Proposition():
    embed_message = discord.Embed()
    title, author, start_time = "" , "" , None
    color = 0x0055ff

    ayes, nays = [], []
    voting_members = []
    status = "Voting..."

    def __init__(self, title, author, start_time, voting_members):
        self.title = title
        self.author = author
        self.start_time = start_time

        self.ayes, self.nays = [], []

        self.voting_members = voting_members

    def get_embed(self):
        self.embed_message = discord.Embed()

        self.embed_message.title = self.title
        self.embed_message.color = self.color
        self.embed_message.add_field(name="Author", value=self.author, inline=True)

        strStartTime = self.start_time.strftime("%H:%M:%S")
        strEndTime = (self.start_time + timedelta(hours=1)).strftime("%H:%M:%S")
        self.embed_message.add_field(name="Start Time", value=strStartTime, inline=True)
        self.embed_message.add_field(name="End Time", value=strEndTime, inline=True)

        if(self.status != "Voting..."): # don't reveal public votes until the end
            ayeText, nayText = "\n".join(self.ayes), "\n".join(self.nays)
            if(ayeText == ""):
                ayeText = "No voters yet!"
            if(nayText == ""):
                nayText = "No voters yet!"

            self.embed_message.add_field(name="Ayes", value=ayeText, inline=False)
            self.embed_message.add_field(name="Nays", value=nayText, inline=False)
        else: # voting is still happening -- reveal non-voted members
            non_voting_members = [str(m) for m in self.voting_members if(str(m) not in self.ayes and str(m) not in self.nays)]
            self.embed_message.add_field(name="Currently Voting Members", value="\n".join(non_voting_members), inline=False)

        self.embed_message.set_footer(text="Status: {}".format(self.status))
        return self.embed_message
