import discord
import requests
import string
import aiohttp
from discord.utils import get
from discord.ext import commands, tasks
import json
import mysql.connector
from mysql.connector import errorcode

client = commands.Bot(command_prefix = '--')
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
        cnx = mysql.connector.connect(user=sql['user'], password=sql['pass'],
                                  host=sql['host'],
                                  database=sql['database'])
    except mysql.connector.Error as err:
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

@client.event
async def on_message(message):


    if message.content.startswith('--emote'):
        guildID = message.guild.id
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
            approve = get_emote(client.guilds, ':approve:')
            await emoteMsg.add_reaction(approve)
            deny = get_emote(client.guilds, ':deny:')
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
                cnx = mysql.connector.connect(user=sql['user'], password=sql['pass'],
                                              host=sql['host'],
                                              database=sql['database'])
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
            else:
                cursor = cnx.cursor

                voteQuery = ("INSERT INTO emoteVotes"
                             "(emoteName,emoteLink,emoteID,voteStatus,guildID)"
                             "VALUES(%s, %s, %s, %s, %s)")
                voteData = (name, url, emoteMsg.id, "In Voting", guildID)

                cursor.execute(voteQuery, voteData)
                cnx.commit()
                cursor.close()
                cnx.close()



            await emoteMsg.edit(embed=newMsg)

        elif sub.startswith('approve'):
            id = sub.split('approve')[1]
            id = id.translate({ord(c): None for c in string.whitespace})

            msg = await getmsg(message.channel, id)

            print(msg.content)
            # response = requests.get(url)
            # emoji = await message.channel.guild.create_custom_emoji(name=name, image=response.content)
            # print("Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!".format(emoji,
            #                                                                             "a" if emoji.animated else ""))

        elif sub.startswith('deny'):
            print('Emote Denied')

        else:
            msg = discord.Embed(title="Emote help",
                                description="To request a new emote use --emote add <name> and attach an image\n "
                                            "To Approve an emote request (Admin only) use --emote approve <VoteID>\n "
                                            "To Deny an Emote Request (Admin only) use --emote deny <VoteID>",
                                color=discord.Color.blue())
            await message.channel.send(embed=msg)









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
