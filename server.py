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

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
token = ''
sql = {}
cnx = ''


def init():
    global token
    global sql

    f = open('config/bot.json')
    data = json.load(f)
    token = data['token']
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
    message = msg

    guildID = message.guild.id

    if message.content.startswith('--emote'):

        sub = message.content.split('--emote')[1]
        sub = sub.translate({ord(c): None for c in string.whitespace})
        if sub.startswith('add'):
            name = sub.split('add')[1]
            name = name.translate({ord(c): None for c in string.whitespace})
            url = message.attachments[0].url
            msg = discord.Embed(title="Emote Vote",
                                description=str(message.author.mention) + " Is requesting this emote be added",
                                color=discord.Color.blue())
            msg.set_thumbnail(url=url)
            msg.add_field(name="Emote Name", value=name,
                          inline=False)
            emoteMsg = await message.channel.send(embed=msg)
            approve = get_emote(client.guilds, ':yes:')
            await emoteMsg.add_reaction(approve)
            deny = get_emote(client.guilds, ':no:')
            await emoteMsg.add_reaction(deny)

            newMsg = discord.Embed(title="Emote Vote",
                                   description=str(message.author.mention) + " Is requesting this emote be added",
                                   color=discord.Color.blue())
            newMsg.set_thumbnail(url=url)
            newMsg.add_field(name="Emote Name", value=name,
                             inline=False)
            newMsg.add_field(name="Vote ID", value=emoteMsg.id)
            newMsg.add_field(name="Vote Status", value="In Voting")

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

                voteQuery = ("INSERT INTO emoteVotes"
                             "(emoteName,emoteLink,emoteID,voteStatus,guildID)"
                             "VALUES(%s, %s, %s, %s, %s)")
                voteData = (name, url, emoteMsg.id, "In Voting", guildID)

                cursor.execute(voteQuery, voteData)
                cnx.commit()
                cursor.close()
                cnx.close()

            await emoteMsg.edit(embed=newMsg)
            await message.delete()

        elif sub.startswith('approve'):
            if "staff" in [y.name.lower() for y in message.author.roles]:
                id = sub.split('approve')[1]
                id = id.translate({ord(c): None for c in string.whitespace})
                url = ''
                name = ''
                channel = message.channel
                msg = await channel.fetch_message(id)

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

                    voteQuery = f"SELECT emoteName,emoteLink FROM emoteVotes WHERE (emoteID = '{id}' AND guildID = '{guildID}')"
                    voteData = (id)
                    print(voteQuery)
                    cursor.execute(voteQuery)
                    data = cursor.fetchall()
                    print(data)

                    if cursor.rowcount > 0:
                        for (emoteName, emoteLink) in cursor:
                            name = emoteName
                            url = emoteLink

                        cursor.close()
                        cnx.close()

                        print(name)
                        print(url)

                        # newMsg = discord.Embed(title="Emote Vote",
                        #                        description=str(message.author.mention) + " Is requesting this emote be added",
                        #                        color=discord.Color.blue())
                        # newMsg.set_thumbnail(url=url)
                        # newMsg.add_field(name="Emote Name", value=name,
                        #                  inline=False)
                        # newMsg.add_field(name="Vote ID", value=id)
                        # newMsg.add_field(name="Vote Status", value="Closed")
                        # await msg.edit(embed=newMsg)

                        try:
                            fname = url.split('/')[-1]
                            response = requests.get(url)

                            open(fname, 'wb').write(response.content)
                            fSize = int(os.path.getsize(fname))
                            if fSize > 262144:
                                emote = Image.open(fname)
                                emote = emote.resize((128, 128), Image.ANTIALIAS)
                                emote.save(fname, optimize=True, quality=85)
                                fSize = int(os.path.getsize(fname))
                                print(fSize)
                                with open(fname, 'rb') as fd:
                                    emoji = await message.guild.create_custom_emoji(name=name, image=fd.read())

                                await message.channel.send(
                                    "Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!"
                                        .format(emoji, "a" if emoji.animated else ""))
                                os.remove(fname)

                            else:
                                emoji = await message.channel.guild.create_custom_emoji(name=name,
                                                                                        image=response.content)
                                await message.channel.send(
                                    "Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!"
                                        .format(emoji, "a" if emoji.animated else ""))
                        except:
                            await message.channel.send("failed to add the emoji")
                        await message.delete()
                    else:
                        await message.channel.send("Invalid VoteID")
            else:
                await message.channel.send("This Command is reserved for Staff Members")


        elif sub.startswith('deny'):
            # role = discord.utils.find(lambda r: r.name == 'Staff', message.server.roles)
            if "staff" in [y.name.lower() for y in message.author.roles]:
                id = sub.split('deny')[1]
                id = id.translate({ord(c): None for c in string.whitespace})
                await message.channel.send(f"Request to add the emoji (Vote ID: {id} denied! ")
                await message.delete()
            else:
                await message.channel.send("This Command is reserved for Staff Members")

        else:
            msg = discord.Embed(title="Emote help",
                                description="To request a new emote use --emote add <name> and attach an image\n "
                                            "To Approve an emote request (Admin only) use --emote approve <VoteID>\n "
                                            "To Deny an Emote Request (Admin only) use --emote deny <VoteID>",
                                color=discord.Color.blue())
            await message.channel.send(embed=msg)

    if message.content.startswith('--ask'):
        sub = message.content.split('--ask')[1]
        sub = sub.translate({ord(c): None for c in string.whitespace})
        # user = discord.utils.get(client.users, name=sub)
        # print(sub)
        # if user is None:
        #     print("User not found")
        # else:
        #     print(user)
        msg = discord.Embed(title="DM Request",
                            description=f"{str(message.author.mention)} would like to DM {sub}",
                            color=discord.Color.blue())
        dmRequest = await message.channel.send(embed=msg)
        approve = get_emote(client.guilds, ':voteYes:')
        await dmRequest.add_reaction(approve)
        deny = get_emote(client.guilds, ':voteNo:')
        await dmRequest.add_reaction(deny)

        await message.delete()

    if message.content.startswith('--verify'):
        sub = message.content.split('--verify')[1]
        sub = sub.translate({ord(c): None for c in string.whitespace})

        if sub.startswith("cross"):
            sub2 = message.content.split('cross')[1]
            sub2 = sub2.translate({ord(c): None for c in string.whitespace})

            if sub2.startswith("list"):
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

                    voteQuery = f"SELECT id,guildName FROM `cross` WHERE guildID = '{guildID}'"
                    print(voteQuery)
                    cursor.execute(voteQuery)
                    data = cursor.fetchall()
                    print(data)

                    if cursor.rowcount > 0:
                        cross = {}
                        for (id, guildName) in data:
                            cross[id] = f"{guildName}"

                        cursor.close()
                        cnx.close()

                        print(cross)
                        newline = "\n"
                        msg = discord.Embed(title="Cross Verifiable Servers",
                                            description=f'{newline.join(f"[{key}] - {value}" for key, value in cross.items())}',
                                            color=discord.Color.blue())
                        crossMsg = await message.channel.send(embed=msg)
                    else:
                        await message.channel.send("Failed to display Cross List")
                    await message.delete()

            if sub2.startswith('add'):
                if "Partner Manager" in [y.name.lower() for y in message.author.roles]:
                    name = sub.split('add')[1:]
                    guildName = ""
                    for a in name:
                        guildName = guildName + ' ' + a

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

                        voteQuery = ("INSERT INTO `cross`"
                                     "(guildName,guildID)"
                                     "VALUES(%s, %s)")
                        voteData = (guildName, guildID)

                        cursor.execute(voteQuery, voteData)
                        cnx.commit()
                        cursor.close()
                        cnx.close()
                        await message.channel.send(f"{guildName} Successfully added to the Cross Verify List")
                    await message.delete()
                else:
                    await message.channel.send("This Command is reserved for Staff Members")

            if sub2.startswith('revoke'):
                if "Partner Manager" in [y.name.lower() for y in message.author.roles]:
                    id = sub.split('revoke')[1:]
                    guildName = ""
                    for a in id:
                        guildName = guildName + ' ' + a

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

                        voteQuery = (f"DELETE FROM `cross` WHERE id = {guildName}")

                        cursor.execute(voteQuery)
                        cnx.commit()
                        cursor.close()
                        cnx.close()
                        await message.channel.send(f"{guildName} Successfully removed from the Cross Verify List")
                    await message.delete()
                else:
                    await message.channel.send("This Command is reserved for Staff Members")

        if message.mentions:
            if "verifier" in [y.name.lower() for y in message.author.roles]:
                for user in message.mentions:
                    try:
                        verified = get(user.guild.roles, name="✨VERIFIED✨")
                        unverified = get(user.guild.roles, name="Unverified")
                        await user.add_roles(verified)
                        await user.remove_roles(unverified)
                        await message.channel.send(f"Successfully gave {user} the role: ✨VERIFIED✨")
                    except Exception as e:
                        await message.channel.send(f"Failed to give {user} the role: ✨VERIFIED✨")
                        print(e)
            else:
                await message.channel.send("This Command is reserved for Verifying Staff Members")
        elif not sub:
            msg = discord.Embed(title="Verify help",
                                description="---------CROSS VERIFY------------\n"
                                            "To View Cross Verifiable servers user --verify cross list\n"
                                            "To Add Cross Verifiable servers user --verify cross add <server Name>\n"
                                            "To Remove Cross Verifiable servers user --verify cross revoke <server Name>\n"
                                            "-------------VERIFY---------------\n"
                                            "To Verify a user use --verify @user",
                                color=discord.Color.blue())
            await message.channel.send(embed=msg)

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
    await log(msg)
    # to avoid 'commands not working'
    # await client.process_commands(msg)


async def log(msg):
    # get the guild from the message
    guild = msg.guild
    channelID = msg.channel.id
    # find the channel with name 'logs'
    log_channel = discord.utils.get(guild.channels, name="server-logs")
    if msg.channel.name != "server-logs":
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
                        logMsg.set_image(url=file.url)


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

@client.event
async def on_reaction_add(reaction, user):
    print(reaction.message)
    newMsg = discord.Embed(title="Emote Vote",
                           description=f"{str(reaction.author.mention)} would like to DM {sub}",
                           color=discord.Color.blue())


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
client.run(token)
