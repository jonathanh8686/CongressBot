#!/usr/bin/env python3

from discord.ext import commands
import json
import discord
from datetime import datetime
from time import gmtime, strftime
from threading import Timer

bot = commands.Bot(command_prefix="-")

cogs = ["voting"]
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

@bot.command()
async def changelog(ctx):
    changelog_embed = discord.Embed(title="CongressBot Changelog")
    changelog_embed.description = "12/29/2019 - v1.1"

    changelog_embed.color = 0x03fc6f
    changelog_embed.add_field(name="Forced Quits", value="Anyone with the ADMINISTRATOR permission can now force end a proposition (freezing the vote and ending the voting period).")
    changelog_embed.add_field(name="Congress Adjourned", value="CongressBot will no longer accept new propositions after 10PM and before 8AM")
    changelog_embed.add_field(name="Protected voting", value="Voting sides are no longer revealed before the final decision of a proposition has been made")
    changelog_embed.add_field(name="Time's Up", value="Propositions that have reached the end of the 1 hour voting period without all members voting will be passed/rejected if there is a quorum of 66%")
    changelog_embed.add_field(name="Time is right", value="Timezones of Congress are always be to from PST -- Start/End times fixed.")


    await ctx.send(embed=changelog_embed)

    await ctx.message.delete()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if(message.channel.id != 287438361528893442):
        return

    #if(datetime.now().hour > 22 or datetime.now().hour < 8): # congress adjourns from 10pm to 8am
    #    return

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\t" + str(message.author) + ":\t" + message.content) # record the messages sent
    await bot.process_commands(message)

configData = json.loads(open("config.json", "r").read())

for c in cogs:
    bot.load_extension(c)
bot.run(configData["bot_token"])
