import discord
from config import Config
import logging
import random
import datetime
import asyncio.exceptions
import discord.errors

client = discord.Client()
logging.basicConfig(level=logging.INFO, filename='discord_output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.info("Bot started succesfully.")

#mod_role_name = [The Asian Squad - GrandBotMaster, Ascenion - Admin]
MOD_ROLE_ID = [706468834235645954, 100920245190946816]


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Monster Hunter World"))
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
######## USER COMMANDS ###############

    if message.content.startswith('/addsession'):
        channel = client.get_channel(706521000640249927) #asian squad
        #channel = client.get_channel(619171183006580767) #ascension testing
        now = datetime.datetime.now().strftime('%d %b %I:%M %p')
        prompt_session_id, prompt_session_title, session_id_reply, session_title_reply = None,None,None,None
        try:
            content = message.content[12:]
            if content == "":
                prompt_session_id = await message.channel.send('Creating session.. Whats the session ID?', delete_after=90.0)
                def check_session_id(m):
                    return m.channel == message.channel and m.author == message.author
                session_id_reply = await client.wait_for('message', check=check_session_id, timeout=90.0)
                session = session_id_reply.content

                prompt_session_title = await message.channel.send('Enter session description? (Type `cancel` if no description)', delete_after=90.0)
                def check_session_title(m):
                    return m.channel == message.channel and m.author == message.author
                session_title_reply = await client.wait_for('message', check=check_session_title, timeout=90.0)

                if session_title_reply.content.lower() == 'cancel':
                    session_title = 'Monster Hunting'
                else:
                    session_title = session_title_reply.content

                await message.channel.send('Session created in {}'.format(channel.mention), delete_after=5.0)
            else:
                session = "".join(content.split())
                session = session[:4] + ' ' + session[4:8] + ' ' + session[8:12]
                session_title = 'Monster Hunting'
            title = '{}'.format(session_title)
            session_id = '```fix\n{}```'.format(session)
            embed = discord.Embed(description='```yaml\n{}```'.format(title), color=0xf1c40f)
            embed.add_field(name='Session ID', value=session_id)
            embed.set_footer(text='Added on {}'.format(now))
            embed.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
            msg = await channel.send(embed=embed)
            cemoji = await message.guild.fetch_emoji(707541604508106818)  #custom emoji to mark session close
            await msg.add_reaction(cemoji)
            await message.delete()
        except asyncio.exceptions.TimeoutError:
            logging.info('{} timed out when creating new session.'.format(message.author.display_name))
            await message.channel.send('{} timed out when creating new session.'.format(message.author.display_name), delete_after=5.0)
            pass
        finally:
            if prompt_session_id is not None:
                await prompt_session_id.delete()
                await session_id_reply.delete()
            if prompt_session_title is not None:
                await prompt_session_title.delete()
                await session_title_reply.delete()

    elif message.content.startswith('/addlfg'):
        channel = message.channel
        await message.delete()
        event_button = await message.guild.fetch_emoji(707790768324083732)
        siege_button = await message.guild.fetch_emoji(707790900927135765)
        msg = await channel.send('Click the following buttons to post a LFG/schedule a siege.\n'
                                 '{} for event, {} for siege.'.format(event_button, siege_button))
        await msg.add_reaction(event_button)
        await msg.add_reaction(siege_button)


    elif message.content.startswith('/help'):
        content = 'Available commands are: \n' \
                  '`/addsession <session_id>` - Adds a session with the given session ID \n' \
                  '`/addsession` - Bot will prompt you on what is the session ID \n' \
                  '`/help` - This help message.'
        await message.channel.send(content)

    # elif message.content.startswith('!test'):
    #     msg_id = int(message.content[6:])
    #     chnl = await client.fetch_channel(706466658373599253)
    #     msg = await chnl.fetch_message(msg_id)
    #     time_edited = msg.created_at
    #     print(time_edited.strftime('%I:%M:%S %p'))



############## ADMIN COMMANDS ###################

    elif message.content.startswith('&logoff'):
        member = message.author
        top_role = member.top_role
        if top_role.id not in MOD_ROLE_ID:
            return
        else:
            await message.delete()
            await client.close()

    elif message.content.startswith('&announce'):
        member = message.author
        ask_reaction = True
        reaction_list = []
        top_role = member.top_role
        if top_role.id not in MOD_ROLE_ID:
            return
        else:
            prompt_pin_message = await message.channel.send('What is the content of pinned message?', delete_after=60.0)
            def check_msg(m):
                return m.channel == message.channel and m.author == message.author
            pinned_message = await client.wait_for('message', check=check_msg, timeout=60.0)

            while ask_reaction is True:
                prompt_reaction = await message.channel.send('Send me a emoji for the reaction(type `cancel` to cancel reaction adding.)', delete_after=60.0)

                def check_emoji(m):
                    return m.channel == message.channel and m.author == message.author
                reaction_check = await client.wait_for('message', check=check_emoji, timeout=60.0)

                if reaction_check.content != 'cancel':
                    reaction = reaction_check
                    await reaction_check.delete()
                    await prompt_reaction.delete()
                    reaction_list.append(reaction.content)
                else:
                    msg = await message.channel.send(pinned_message.content)
                    await reaction_check.delete()
                    await prompt_reaction.delete()
                    for r in reaction_list:
                        try:
                            await msg.add_reaction(r)
                        except:
                            pass
                    ask_reaction = False
            await prompt_pin_message.delete()
            await pinned_message.delete()
            await message.delete()

    elif message.content.startswith('&addreact'):
        member = message.author
        top_role = member.top_role
        ask_reaction = True
        reaction_list = []
        if top_role.id not in MOD_ROLE_ID:
            return
        else:
            try:
                prompt_msg_id = await message.channel.send('What is the message ID?')

                def check_id(m):
                    return m.author == message.author and m.channel == message.channel

                msg_id = await client.wait_for('message', check=check_id, timeout=60.0)

                while ask_reaction is True:
                    prompt_reaction = await message.channel.send('Send me a emoji for the reaction(type `cancel` to cancel reaction adding.)', delete_after=60.0)

                    def check_emoji(m):
                        return m.channel == message.channel and m.author == message.author
                    reaction_check = await client.wait_for('message', check=check_emoji, timeout=60.0)

                    if reaction_check.content != 'cancel':
                        reaction = reaction_check
                        await reaction_check.delete()
                        await prompt_reaction.delete()
                        reaction_list.append(reaction.content)
                    else:
                        msg = await message.channel.fetch_message(int(msg_id.content))
                        await reaction_check.delete()
                        await prompt_reaction.delete()
                        for r in reaction_list:
                            try:
                                await msg.add_reaction(r)
                            except:
                                pass
                        ask_reaction = False
            except TimeoutError:
                logging.info('{} timeout when using &addreact'.format(member.name))
            finally:
                try:
                    await prompt_msg_id.delete()
                    await msg_id.delete()
                except discord.errors.NotFound:
                    pass
                except UnboundLocalError:
                    pass
        await message.delete()

    elif message.content.startswith('&setsosmessage'):
        member = message.author
        top_role = member.top_role
        if top_role.id not in MOD_ROLE_ID:
            return
        else:
            prompt_sos_msg = await message.channel.send('What is the new sos message?')
            def check_sos_msg(m):
                return m.channel == message.channel and m.author == message.author

            new_sos_msg = await client.wait_for('message', check=check_sos_msg, timeout=30.0)

            prompt_msg_id = await message.channel.send('What is the message id of the pinned sos message?')

            def check_msg_id(m):
                return m.channel == message.channel and m.author == message.author
            msg_id_content = await client.wait_for('message', check=check_msg_id, timeout=30.0)
            msg_id = int(msg_id_content.content)

            msg = await message.channel.fetch_message(msg_id)
            await msg.edit(content=new_sos_msg.content)
            await prompt_sos_msg.delete()
            await prompt_msg_id.delete()
            await new_sos_msg.delete()
            await msg_id_content.delete()

@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    channel_id = payload.channel_id
    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    user = client.get_user(payload.user_id)
    bot_added_reactions = message.reactions #reactions that was added by bot in message
    if payload.emoji.is_custom_emoji() is True: #if user add emoji is custom
        emoji_add = payload.emoji.id  #set emoji_add to emoji id
    else:
        emoji_add = payload.emoji.name #else set to emoji name

    list_of_reactions = []

    for reaction in bot_added_reactions:
        if reaction.me:
            try:
                list_of_reactions.append(reaction.emoji.id) #if can get emoji id means custom emoji
            except AttributeError:
                list_of_reactions.append(reaction.emoji) #if not is unicode emoji

    if message.author.id == user.id:
        return

    if emoji_add in list_of_reactions:
        if emoji_add == '✅' and message_id == 706491925649424434: #rules messsage id
            rules_message = await channel.fetch_message(706491925649424434)
            member = payload.member
            guild = message.guild
            new_fiver = guild.get_role(706870296334041088)
            await member.remove_roles(new_fiver)
            await rules_message.remove_reaction('✅', member)

        elif emoji_add == 707790768324083732:   #create event :zinsigh:
            member = payload.member
            cemoji = await message.guild.fetch_emoji(707790768324083732)
            quest_board_channel = message.guild.get_channel(708369949831200841)

            try:
                prompt_event_title = await message.channel.send('{} Whats the objective?(Type `cancel` to stop)'.format(member.mention), delete_after=60.0)
                def check_event(m):
                    return m.author == member and m.channel == channel
                event_title = await client.wait_for('message', check=check_event, timeout=60.0)
                if event_title.content.lower() == 'cancel':
                    return
                prompt_time = await message.channel.send('{} What time is preferred?(Type `NA` if no preference, `cancel` to stop.)'.format(member.mention), delete_after=60.0)
                def check_time(m):
                    return m.author == member and m.channel == message.channel
                event_time = await client.wait_for('message', check=check_time, timeout=60.0)
                if event_time.content.lower() == 'cancel':
                    await event_time.delete()
                    return
                elif event_time.content.lower() == 'na':
                    event_time.content = '--'
                event_title_description = '```fix\n{}\n```'.format(event_title.content)
                e = discord.Embed(description=event_title_description)
                e.add_field(name='Time (GMT+8)', value=event_time.content, inline=False)
                e.add_field(name='Hunters: 1', value=member.name, inline=False)
                e.set_footer(text='Click 👍 to join/unjoin event, ❌ to close event.')
                e.set_author(name=member.display_name, icon_url=member.avatar_url)
                msg = await quest_board_channel.send(embed=e)
                await msg.add_reaction('👍')
                await msg.add_reaction('❌')
                await message.channel.send('LFG has been posted at {}.'.format(quest_board_channel.mention),delete_after=5.0)
            except asyncio.exceptions.TimeoutError:
                await message.channel.send('Creating of post timed out. Please try again.', delete_after=5.0)
                logging.info('{} timed out when creating new event.'.format(member.mention))
                pass
            finally:
                try:
                    await message.remove_reaction(cemoji, member)
                    await prompt_event_title.delete()
                    await event_title.delete()
                    await prompt_time.delete()
                    await event_time.delete()
                except discord.errors.NotFound:
                    pass
                except UnboundLocalError:
                    pass


        elif emoji_add == 707790900927135765:   #create siege :xenoeyes:
            cemoji = await message.guild.fetch_emoji(707790900927135765)
            now = datetime.datetime.now().strftime('%d %b %I:%M %p')
            member = payload.member
            quest_board_channel = message.guild.get_channel(708369949831200841)

            prompt_siege = await message.channel.send('❗ for Safi jiiva siege, ‼️ for Kulve Taroth siege.', delete_after=30.0)
            await prompt_siege.add_reaction('❗')
            await prompt_siege.add_reaction('‼️')
            try:
                def check_siege(reaction, user):
                    return user==payload.member and (str(reaction.emoji) == '❗' or str(reaction.emoji) == '‼️')

                siege_reaction, member = await client.wait_for('reaction_add', check=check_siege, timeout=30.0)
                await prompt_siege.delete()

                if str(siege_reaction) == '❗':
                    siege_monster = "Safi'jiiva"
                else:
                    siege_monster = 'Kulve Taroth'

                prompt_time = await message.channel.send('{}, What is the time for siege? (Type `NA` if no time preference, `cancel` to stop)'.format(member.mention))

                def check_time(m):
                    return m.author == member and m.channel == channel

                siege_time = await client.wait_for('message', check=check_time, timeout=30.0)

                if siege_time.content.lower() == 'cancel':
                    return
                elif siege_time.content.lower() == 'na':
                    siege_time.content = '--'

                siege_monster_desc = '```fix\n{}\n```'.format(siege_monster)
                e = discord.Embed(description=siege_monster_desc)
                e.add_field(name='Time (GMT+8)', value=siege_time.content, inline=False)
                e.add_field(name='Hunters: 1', value=member.name, inline=False)
                e.set_footer(text='Click 👍 to join/leave siege, ❌ to close siege.')
                if siege_monster == "Safi'jiiva":
                    e.set_thumbnail(url='https://vignette.wikia.nocookie.net/monsterhunter/images/f/fa/MHWI-Safi%27jiiva_Icon.png/revision/latest/scale-to-width-down/340?cb=20191207161325')
                else:
                    e.set_thumbnail(url='https://ih0.redbubble.net/image.551722156.9913/flat,550x550,075,f.u3.jpg')
                e.set_author(name=member.display_name, icon_url=member.avatar_url)
                msg = await quest_board_channel.send(embed=e)
                await msg.add_reaction('👍')
                await msg.add_reaction('❌')

                await channel.send('LFG has been posted at {}.'.format(quest_board_channel.mention), delete_after=5.0)
            except asyncio.exceptions.TimeoutError:
                await message.channel.send('Creating of post timed out. Please try again.', delete_after=5.0)
                logging.info('{} timed out when creating new siege.'.format(member.mention))
                pass
            finally:
                try:
                    await message.remove_reaction(cemoji, member)
                    await prompt_time.delete()
                    await siege_time.delete()
                except discord.errors.NotFound:
                    pass


        elif emoji_add == '👍':
            member_name = payload.member.name
            embed = message.embeds[0]
            fields = embed.fields
            players = fields[1].value
            list_of_players = players.split()
            if member_name not in list_of_players:
                list_of_players.append(member_name)
                new_players = '\n'.join(list_of_players)
                no_of_players = len(list_of_players)
                embed.set_field_at(1, name='Hunters: {}'.format(no_of_players), value=new_players, inline=False)
                await message.edit(embed=embed)

        elif emoji_add == 707541604508106818:   #mark session closed :fail:
            await channel.send('Session ID deleted..', delete_after=5.0)
            await message.delete()

        elif emoji_add == '❌':
            member = payload.member
            embed = message.embeds[0]
            fields = embed.fields
            players = fields[1].value
            host = players.split()[0]
            if member.name == host:
                await channel.send('Post deleted..', delete_after=5.0)
                await message.delete()
            else:
                await channel.send('{}, Post can only be deleted by the 1st hunter in the list.'.format(member.mention), delete_after=5.0)
                await message.remove_reaction('❌', payload.member)



@client.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    channel_id = payload.channel_id
    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    emoji_remove = payload.emoji.name
    user = client.get_user(payload.user_id)
    bot_added_reactions = message.reactions
    list_of_reactions = []

    for reaction in bot_added_reactions:
        list_of_reactions.append(reaction.emoji)

    if message.author.id == user.id:
        return

    if emoji_remove in list_of_reactions:
        if emoji_remove == '👍':
            try:
                member_name = user.name
                embed = message.embeds[0]
                fields = embed.fields
                players = fields[1].value
                list_of_players = players.split()
                if member_name in list_of_players:
                    list_of_players.remove(member_name)
                    new_players = ('\n').join(list_of_players)
                    no_of_players = len(list_of_players)
                    embed.set_field_at(1, name='Hunters: {}'.format(no_of_players), value=new_players, inline=False)
                    await message.edit(embed=embed)
            except discord.errors.HTTPException:
                pass

# @client.event
# async def on_member_join(member):
#     guild = client.get_guild(706463594719608883)
#     new_fiver = guild.get_role(706870296334041088)
#     newcomer = member.mention
#     channel = client.get_channel(706463594719608886)
#     general_channel = client.get_channel(706466658373599253)
#     session_id_channel = client.get_channel(706521000640249927)
#     read_first_channel = client.get_channel(706477462183346277)
#     welcome_list = ["Keep your palicoes! {} is here to hunt!!".format(newcomer),
#                     "{} is here to slay some Great Jagras!".format(newcomer),
#                     "Here comes {}, the Rajang(ahem Rajunk) slayer!".format(newcomer),
#                     "Welcome {} to the Gathering Hall.".format(newcomer),
#                     "Thank the Elder dragons. {} is here to save us from Safi'jiiva!".format(newcomer),
#                     "🐋 cum {} to the hunting hall.".format(newcomer),
#                     "{} is here to cook us some raw meat.".format(newcomer)]
#     index = random.randrange(0, len(welcome_list), 1)
#     await channel.send('{}\nMake sure to read {}, drop by {} to say hi, and join our squad sessions at {}'.format(welcome_list[index],read_first_channel.mention, general_channel.mention, session_id_channel.mention))
#     await member.add_roles(new_fiver)

# run discord bot
client.run(Config.discord_token)