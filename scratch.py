 # if message.content.startswith('--emote'):

    #     sub = message.content.split('--emote')[1]
    #     sub = sub.translate({ord(c): None for c in string.whitespace})
    #     if sub.startswith('add'):
    #         name = sub.split('add')[1]
    #         name = name.translate({ord(c): None for c in string.whitespace})
    #         url = message.attachments[0].url
    #         msg = discord.Embed(title="Emote Vote",
    #                             description=str(message.author.mention) + " Is requesting this emote be added",
    #                             color=discord.Color.blue())
    #         msg.set_thumbnail(url=url)
    #         msg.add_field(name="Emote Name", value=name,
    #                       inline=False)
    #         emoteMsg = await message.channel.send(embed=msg)
    #         approve = get_emote(client.guilds, ':yes:')
    #         await emoteMsg.add_reaction(approve)
    #         deny = get_emote(client.guilds, ':no:')
    #         await emoteMsg.add_reaction(deny)

    #         newMsg = discord.Embed(title="Emote Vote",
    #                                description=str(message.author.mention) + " Is requesting this emote be added",
    #                                color=discord.Color.blue())
    #         newMsg.set_thumbnail(url=url)
    #         newMsg.add_field(name="Emote Name", value=name,
    #                          inline=False)
    #         newMsg.add_field(name="Vote ID", value=emoteMsg.id)
    #         newMsg.add_field(name="Vote Status", value="In Voting")

    #         try:
    #             cnx = mysql.connect(user=sql['user'], password=sql['pass'],
    #                                 host=sql['host'],
    #                                 database=sql['database'])
    #         except mysql.Error as err:
    #             if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    #                 print("Something is wrong with your user name or password")
    #             elif err.errno == errorcode.ER_BAD_DB_ERROR:
    #                 print("Database does not exist")
    #             else:
    #                 print(err)
    #         else:
    #             cursor = cnx.cursor()

    #             voteQuery = ("INSERT INTO emoteVotes"
    #                          "(emoteName,emoteLink,emoteID,voteStatus,guildID)"
    #                          "VALUES(%s, %s, %s, %s, %s)")
    #             voteData = (name, url, emoteMsg.id, "In Voting", guildID)

    #             cursor.execute(voteQuery, voteData)
    #             cnx.commit()
    #             cursor.close()
    #             cnx.close()

    #         await emoteMsg.edit(embed=newMsg)
    #         await message.delete()

    #     elif sub.startswith('approve'):
    #         if "staff" in [y.name.lower() for y in message.author.roles]:
    #             id = sub.split('approve')[1]
    #             id = id.translate({ord(c): None for c in string.whitespace})
    #             url = ''
    #             name = ''
    #             channel = message.channel
    #             msg = await channel.fetch_message(id)

    #             try:
    #                 cnx = mysql.connect(user=sql['user'], password=sql['pass'],
    #                                     host=sql['host'],
    #                                     database=sql['database'])
    #             except mysql.Error as err:
    #                 if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    #                     print("Something is wrong with your user name or password")
    #                 elif err.errno == errorcode.ER_BAD_DB_ERROR:
    #                     print("Database does not exist")
    #                 else:
    #                     print(err)
    #             else:
    #                 cursor = cnx.cursor()

    #                 voteQuery = f"SELECT emoteName,emoteLink FROM emoteVotes WHERE (emoteID = '{id}' AND guildID = '{guildID}')"
    #                 voteData = (id)
    #                 print(voteQuery)
    #                 cursor.execute(voteQuery)
    #                 data = cursor.fetchall()
    #                 print(data)

    #                 if cursor.rowcount > 0:
    #                     for (emoteName, emoteLink) in cursor:
    #                         name = emoteName
    #                         url = emoteLink

    #                     cursor.close()
    #                     cnx.close()

    #                     print(name)
    #                     print(url)

    #                     # newMsg = discord.Embed(title="Emote Vote",
    #                     #                        description=str(message.author.mention) + " Is requesting this emote be added",
    #                     #                        color=discord.Color.blue())
    #                     # newMsg.set_thumbnail(url=url)
    #                     # newMsg.add_field(name="Emote Name", value=name,
    #                     #                  inline=False)
    #                     # newMsg.add_field(name="Vote ID", value=id)
    #                     # newMsg.add_field(name="Vote Status", value="Closed")
    #                     # await msg.edit(embed=newMsg)

    #                     try:
    #                         fname = url.split('/')[-1]
    #                         response = requests.get(url)

    #                         open(fname, 'wb').write(response.content)
    #                         fSize = int(os.path.getsize(fname))
    #                         if fSize > 262144:
    #                             emote = Image.open(fname)
    #                             emote = emote.resize((128, 128), Image.ANTIALIAS)
    #                             emote.save(fname, optimize=True, quality=85)
    #                             fSize = int(os.path.getsize(fname))
    #                             print(fSize)
    #                             with open(fname, 'rb') as fd:
    #                                 emoji = await message.guild.create_custom_emoji(name=name, image=fd.read())

    #                             await message.channel.send(
    #                                 "Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!"
    #                                     .format(emoji, "a" if emoji.animated else ""))
    #                             os.remove(fname)

    #                         else:
    #                             emoji = await message.channel.guild.create_custom_emoji(name=name,
    #                                                                                     image=response.content)
    #                             await message.channel.send(
    #                                 "Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!"
    #                                     .format(emoji, "a" if emoji.animated else ""))
    #                     except:
    #                         await message.channel.send("failed to add the emoji")
    #                     await message.delete()
    #                 else:
    #                     await message.channel.send("Invalid VoteID")
    #         else:
    #             await message.channel.send("This Command is reserved for Staff Members")


    #     elif sub.startswith('deny'):
    #         # role = discord.utils.find(lambda r: r.name == 'Staff', message.server.roles)
    #         if "staff" in [y.name.lower() for y in message.author.roles]:
    #             id = sub.split('deny')[1]
    #             id = id.translate({ord(c): None for c in string.whitespace})
    #             await message.channel.send(f"Request to add the emoji (Vote ID: {id} denied! ")
    #             await message.delete()
    #         else:
    #             await message.channel.send("This Command is reserved for Staff Members")

    #     else:
    #         msg = discord.Embed(title="Emote help",
    #                             description="To request a new emote use --emote add <name> and attach an image\n "
    #                                         "To Approve an emote request (Admin only) use --emote approve <VoteID>\n "
    #                                         "To Deny an Emote Request (Admin only) use --emote deny <VoteID>",
    #                             color=discord.Color.blue())
    #         await message.channel.send(embed=msg)