from ast import If
import discord
import requests
import string
import aiohttp
from discord.utils import get
from discord.utils import find
from discord.ext import commands, tasks
import json
import mysql.connector as mysql
from mysql.connector import errorcode
from PIL import Image
import re
import os
import urllib.request
import socket

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
token = ''
devToken = ''
sql = {}
cnx = ''

if socket.gethostname() == 'websrv':
    mode = 'prod'
else:
    mode = 'dev'


def init():
    global token
    global sql
    global devToken

    f = open('config/bot.json')
    data = json.load(f)
    token = data['token']
    devToken = data['dev-token']
    f.close()

    f = open('config/sql.json')
    sql = json.load(f)
    f.close()
    f.close()
    sqlInit()


def sqlInit():
    try:
        cnx = mysql.connect(user=sql['user'], password=sql['pass'],
                            host=sql['host'],
                            database=sql['database'],
                            auth_plugin='mysql_native_password')
    except mysql.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()


async def getmsg(ctx, msgID: int):
    msg = await ctx.fetch_message(msgID)
    return msg


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.CustomActivity('Developing KinkyBot'))


# @client.event
# async def on_message(message):

@client.event
async def on_member_join(member):
    print(f"Welcome {member.display_name}")
    guildID = member.guild.id

    try:
        cnx = mysql.connect(user=sql['user'], password=sql['pass'],
                            host=sql['host'],
                            database=sql['database'])
    except mysql.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cursor = cnx.cursor()

        voteQuery = f"SELECT name FROM `user-blacklist` WHERE (name = '{member.display_name.lower()}' AND guildID = '{guildID}')"
        print(voteQuery)
        cursor.execute(voteQuery)
        data = cursor.fetchall()
        print(data)

        if cursor.rowcount > 0:
            try:
                await member.send(
                    "You have been blacklisted from joining this server, to appeal this ban, please join this "
                    "server: https://discord.gg/T3Bmkm9hpf")
                await member.guild.ban(member, reason="Blacklisted")
            except Exception as e:
                print(e)
            cursor.close()
            cnx.close()
        else:
            print("Not in Database ")


@client.event
async def on_message(msg):
    guild = msg.guild
    message = msg

    guildID = message.guild.id

   

    if message.content.startswith('--dm'):
        sub = message.content.split('--dm')[1]
        sub = sub.translate({ord(c): None for c in string.whitespace})
        # user = discord.utils.get(client.users, name=sub)
        # print(sub)
        # if user is None:
        #     print("User not found")
        # else:
        #     print(user)
        for user in message.mentions:
            msg = discord.Embed(title="DM Request",
                            description=f"{str(message.author.mention)} would like to DM {user.mention}",
                            color=discord.Color.blue())
            await message.delete()
            dmRequest = await message.channel.send(embed=msg)
            approve = get_emote(client.guilds, ':voteYes:')
            await dmRequest.add_reaction(approve)
            deny = get_emote(client.guilds, ':voteNo:')
            await dmRequest.add_reaction(deny)

            def check(reaction, reacter):
                if reacter == user:
                    return reaction, reacter
            
            try:
                reaction, reacter = await client.wait_for('reaction_add', check=check)
                
            except Exception as e:
                print(e)
            else:
                print(reacter)
                if not 'KinkBot-Dev#0417' in str(reacter) or not 'KinkyBot#0631' in str(reacter):
                    if reacter == user:
                        print(reaction)
                        if ':voteYes:' in str(reaction) :
                            newMsg = discord.Embed(title="DM Request APPROVED",
                                    description=f"{str(message.author.mention)} your DM request has been approved by {user.mention}",
                                    color=discord.Color.blue())
                            await dmRequest.delete()
                            await message.channel.send(embed=newMsg)

                            dm = f"Your DM request has been approved by {user}"
                            await message.author.send(dm)
                            # author = discord.utils.get(client.users, name=str(message.author))
                            # print(str(message.author))
                            # if author is None:
                            #     print("User not found")
                            # else:
                            #     print(author)
                        elif ':voteNo:' in str(reaction):
                            newMsg = discord.Embed(title="DM Request DENIED",
                                    description=f"{str(message.author.mention)} your DM request has been denied by {user.mention}",
                                    color=discord.Color.blue())
                            await dmRequest.delete()
                            await message.channel.send(embed=newMsg)
                        
                        
                    else:
                        print(f"{reacter} tried to react. {user} was needed")
                        await dmRequest.remove_reaction(reaction, reacter)
            # await client.say("You responded with {}".format(reaction.emoji))

        
        
    # Verification Command
    if message.content.startswith('--verify'):

        if 'verify' in msg.channel.name:
            if message.mentions:
                gen = discord.utils.get(guild.channels, name="general-chat")
                roles = discord.utils.get(guild.channels, name="roles")
                color = discord.utils.get(guild.channels, name="color-roles")
                if "verifier" in [y.name.lower() for y in message.author.roles]:
                    for user in message.mentions:
                        try:
                            verified = get(user.guild.roles, name="✨VERIFIED✨")
                            welcome = get(user.guild.roles, name="Welcome Crew")
                            await user.add_roles(verified)
                            await message.channel.send(f"Successfully gave {user.mention} the role: ✨VERIFIED✨")
                            await message.channel.send(f"{user.mention} Please dont forget to get your {roles.mention} and your {color.mention}!")
                            welcomeMsg = f"{welcome.mention} Please welcome {user.mention} to our kinky little family!"
                            await message.delete()
                            await gen.send(welcomeMsg)
                        except Exception as e:
                            await message.channel.send(f"Failed to give {user} the role: ✨VERIFIED✨")
                            print(e)
                else:
                    await message.channel.send("This Command is reserved for Verifying Staff Members")
            elif not sub:
                msg = discord.Embed(title="Verify help",
                                    description="-------------VERIFY---------------\n"
                                                "To Verify a user use --verify @user",
                                    color=discord.Color.blue())
                await message.channel.send(embed=msg)

    # Staff AFK
    if message.content.startswith('--afk'):
        user = message.author
        userID = user.id
        nick = user.display_name
        afk = True
        try:
            cnx = mysql.connect(user=sql['user'], password=sql['pass'],
                                host=sql['host'],
                                database=sql['database'])
        except mysql.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            cursor = cnx.cursor()

            voteQuery = ("INSERT INTO `afk`"
                         "(userID,userNick,afk,guildID)"
                         "VALUES(%s, %s, %s, %s)")
            voteData = (userID, nick, afk, guildID)

            cursor.execute(voteQuery, voteData)
            cnx.commit()
            cursor.close()
            cnx.close()

            await user.edit(nick=f"{nick}[AFK]")
            await message.channel.send(f"{nick} Is now AFK")
        await message.delete()


    if message.content.startswith('--blacklist'):
        if "Staff" in [y.name.lower() for y in message.author.roles]:
            sub = message.content.split('--blacklist')[1]
            sub = sub.translate({ord(c): None for c in string.whitespace})
            if sub.startswith('user'):
                name = message.content.split('user')[1:]

                try:
                    cnx = mysql.connect(user=sql['user'], password=sql['pass'],
                                        host=sql['host'],
                                        database=sql['database'])
                except mysql.Error as err:
                    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                        print("Something is wrong with your user name or password")
                    elif err.errno == errorcode.ER_BAD_DB_ERROR:
                        print("Database does not exist")
                    else:
                        print(err)
                else:
                    cursor = cnx.cursor()

                    voteQuery = ("INSERT INTO `user-blacklist`"
                                 "(name,guildID)"
                                 "VALUES(%s, %s)")
                    voteData = (name.lower(), guildID)

                    cursor.execute(voteQuery, voteData)
                    cnx.commit()
                    cursor.close()
                    cnx.close()
                    await message.channel.send(f"{name} Has been successfully blacklisted")
                await message.delete()
        else:
            await message.channel.send("This Command is reserved for Staff Members")

    
    # log is a coroutine, so don't forget to await the call
    if type(msg) != discord.embeds.Embed:
        await log(msg)
    # to avoid 'commands not working'
    # await client.process_commands(msg)


async def log(msg):
   # find the channel with name 'logs'
    
    if msg.channel.name != "server-logs":
         # get the guild from the message
        try:
            guild = msg.guild
            channelID = msg.channel.id
            log_channel = discord.utils.get(guild.channels, name="server-logs")
        except Exception as e:
            print(e)
        if "verification" not in msg.channel.name:
            try:
                logMsg = discord.Embed(title="Message Log",
                                       description=msg.content,
                                       color=discord.Color.blue())
                logMsg.add_field(name="Author", value=msg.author.mention,
                                 inline=False)
                logMsg.add_field(name="Channel", value=msg.channel.mention,
                                 inline=False)
                logMsg.add_field(name="Time Stamp", value=str(msg.created_at),
                                 inline=False)
                logMsg.add_field(name="Message ID", value=msg.id, inline=True)
                try:
                    if len(msg.attachments) > 0:
                        file = msg.attachments[0]
                        print(file.url)
                        if not os.path.isdir(msg.channel.name):
                            os.mkdir(msg.channel.name)
                        
                        Imagefile_name = msg.channel.name + '/' + str(msg.id) + '-' + file.filename
                        await file.save(Imagefile_name)
                        # urllib.request.urlretrieve(file.url, Imagefile_name)
                        # logMsg.set_image(url='attachment://'+ file.filename)


                except Exception as e:
                    print(f"Failed to add attachments: {e}")
                await log_channel.send(embed=logMsg)
                    
            except Exception as e:
                # exceptions will be raised if any of those said above, are missing
                print("'server-logs' channel not found, or bot missing permissions")
                print(e)

            try:
                for file in msg.attachments:
                    try:
                        logMsg = discord.Embed(title="Message Log",
                                               description=msg.content,
                                               color=discord.Color.blue())
                        logMsg.add_field(name="Author", value=msg.author.mention,
                                         inline=False)
                        logMsg.add_field(name="Channel", value=msg.channel.mention,
                                         inline=False)
                        logMsg.add_field(name="Time Stamp", value=str(msg.created_at),
                                         inline=False)
                        logMsg.add_field(name="Message ID", value=msg.id, inline=True)
                        try:
                            logMsg.set_image(url=file.url)
                        except Exception as e:
                            print(f"Failed to add attachments: {e}")

                        await log_channel.send(embed=logMsg)
                    except Exception as e:
                        # exceptions will be raised if any of those said above, are missing
                        print("'server-logs' channel not found, or bot missing permissions")
                        print(e)
            except Exception as e:
                print(f"Unable to log additional images: {e}")

# @client.event
# async def on_reaction_add(reaction, user):
#     print(reaction.message)
#     newMsg = discord.Embed(title="Emote Vote",
#                            description=f"{str(reaction.author.mention)} would like to DM {sub}",
#                            color=discord.Color.blue())


def get_emote(guilds, emote):
    """
    Gets a matching emote from the given guild.
    :param guild: The guild to search.
    :type guild: discord.Guild
    :param emote: The full emote string to look for.
    :type emote: str
    :return:
    :rtype: discord.Emoji
    """

    for guild in guilds:
        emote_name = emote.split(':')[1]
        matching_emote = None
        for emote in guild.emojis:
            if emote.name == emote_name:
                matching_emote = emote
        return matching_emote


init()
if mode == 'dev':
    client.run(devToken)
else:
    client.run(token)
