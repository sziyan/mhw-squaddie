import discord
from config import Config
import logging
import random
import datetime
import asyncio.exceptions
import discord.errors
from mongoengine import *
from mongoengine import connect
import re
import time
from querysets import GuidingLandsQuery

client = discord.Client()
logging.basicConfig(level=logging.INFO, filename='discord_output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.info("Bot started succesfully.")
logger = logging.getLogger(__name__)

db = connect('sg', host=Config.host)

class Lfg(Document):
    message_id = IntField(required=True)
    confirmed = ListField(IntField())
    tentative = ListField(IntField())
    time = StringField()
    lfg_type = StringField()

class Player(Document):
    player_id = IntField(required=True)
    display_name = StringField()
    remarks = StringField()
    levels = DictField()
    available = BooleanField(default=False)

    meta = {'queryset_class': GuidingLandsQuery}


#mod_role_name = [The Asian Squad - GrandBotMaster, Ascenion - Admin]
MOD_ROLE_ID = [706468834235645954, 100920245190946816]
GUIDING_LANDS = ['forest', 'wildspire', 'coral', 'rotted', 'volcanic', 'tundra']

async def addlfg(message, lfg_type, description, member, time):
    quest_board_channel = message.guild.get_channel(708369949831200841)
    lfg_description = '```fix\n{}\n```'.format(description)
    e = discord.Embed(description=lfg_description, color=discord.Color.red())
    e.add_field(name='Time (GMT+8)', value=time, inline=False)
    e.add_field(name='Confirmed: 1', value=member.display_name, inline=True)
    e.add_field(name='Tentative: 0', value='-', inline=True)
    if lfg_type == 'siege':
        if description == "Safi'jiiva":
            e.set_thumbnail(
                url='https://vignette.wikia.nocookie.net/monsterhunter/images/f/fa/MHWI-Safi%27jiiva_Icon.png/revision/latest/scale-to-width-down/340?cb=20191207161325')
        else:
            e.set_thumbnail(url='https://ih0.redbubble.net/image.551722156.9913/flat,550x550,075,f.u3.jpg')
    e.set_footer(text='|👍 - Attending |❔ - Tentative | ❌ - Delete | 🚧 - Update |')
    e.set_author(name=member.display_name, icon_url=member.avatar_url)
    msg = await quest_board_channel.send(embed=e)
    #msg = await message.channel.send(embed=e)
    lfg_session = Lfg(message_id=msg.id, confirmed=[member.id], lfg_type=lfg_type)
    await msg.add_reaction('👍')
    await msg.add_reaction('❔')
    await msg.add_reaction('❌')
    await msg.add_reaction('🚧')
    lfg_session.save()
    await message.channel.send('LFG has been posted at {}.'.format(quest_board_channel.mention), delete_after=5.0)
    logger.info('{} added {}.'.format(member.display_name, lfg_type))

async def check_mod(guild, member, baseline=None):
    top_role_position = member.top_role.position
    mod_role_position = []
    for id in MOD_ROLE_ID:
        role = guild.get_role(id)
        if role is not None:
            mod_role_position.append(role.position)
    if baseline is not None:
        role = guild.get_role(baseline)
        if role is not None:
            mod_role_position.append(role.position)
    for pos in mod_role_position:
        if top_role_position >= pos:
            return True
    return False

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="/help for info"))
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    guild = message.guild
    member = message.author

###### FUNCTIONS ###########

    async def add_card():
        display_name = member.display_name
        guiding_lands = GUIDING_LANDS
        gl_levels = {}

        await message.channel.send(
            'Enter a description for your guild card (other options: `skip`, `cancel`')
        def check_desc(m):
            return m.channel == message.channel and m.author == message.author
        desc = await client.wait_for('message', check=check_desc, timeout=120.0)
        if desc.content.lower() == 'skip':
            description = '--'
        elif desc.content.lower() == 'cancel':
            await message.channel.send('Exit guild card creation')
            return
        else:
            description = desc.content
        for lands in guiding_lands:
            await message.channel.send('Enter level of {} (`cancel` to exit)'.format(lands.capitalize()))
            def check_lands(m):
                return m.channel == message.channel and m.author == message.author
            gl_lvl = await client.wait_for('message', check=check_lands, timeout=120.0)
            try:
                if gl_lvl.content.lower() == 'cancel':
                    return
                elif int(gl_lvl.content) > 0 and int(gl_lvl.content) <=7:   #ensure input is between level 1 and 7
                    gl_levels[lands] = int(gl_lvl.content)
                else:
                    await message.channel.send('Incorrect input! Exiting guild card creation..')    #if input is less then 1 or more then 7
                    return
            except ValueError:
                await message.channel.send('Input is not a number! Exiting guild card creation..')  #if input is not a number
                return
        await message.channel.send('Allow other hunters to search for your guild card?(yes or no)')
        def check_avail(m):
            return m.channel == message.channel and m.author == message.author
        avail = await client.wait_for('message', check=check_avail, timeout=120.0)
        avail = avail.content.lower()
        if avail == 'yes':
            available = True
        elif avail == 'false':
            available = False
        else:
            await message.channel.send('Invalid option')
            return
        card = Player(player_id=member.id, display_name=display_name, remarks= description, levels=gl_levels, available=available)
        card.save()
        await showcard(card)

    async def showcard(card):
        if (card.display_name != message.author.display_name) and (card.player_id == message.author.id):
            card.display_name = message.author.display_name
            card.save()
            card.reload()
        description = card.remarks
        player_id = card.player_id
        levels = card.levels
        available = card.available
        card_member = message.guild.get_member(player_id)
        e = discord.Embed(title='Guild Card', description='```fix\n{}\n```'.format(description),
                          color=discord.Color.dark_orange())
        e.set_author(name=card.display_name, icon_url=card_member.avatar_url)
        for land,lvl in levels.items():
            e.add_field(name=land.capitalize(), value=lvl, inline=True)
        e.add_field(name='Availability', value=available)
        await message.channel.send(embed=e)

    async def updatecards(card):
        gl_string = ''
        levels = card.levels
        for lands in GUIDING_LANDS:
            gl_string += '`{}`, '.format(lands.capitalize())
        gl_string = gl_string[:-2]  #because last character is a space(discord feature), 2nd last is a comma
        await message.channel.send('Type the category for update.\nAvailable categories are: `cancel`, `description`, `available`, {}'.format(gl_string))
        def check_option(m):
            return m.author == message.author and m.channel == message.channel
        option = await client.wait_for('message', check=check_option, timeout=120.0)
        option = option.content.lower()
        if option == 'description':
            await message.channel.send('Enter new description')
            def check_desc(m):
                return m.author == message.author and m.channel == message.channel
            description = await client.wait_for('message',check=check_desc, timeout=120.0)
            description = description.content
            card.remarks = description
        elif option == 'available':
            await message.channel.send('Enter `True` or `False` to set your available status.')
            def avail(m):
                return m.author == message.author and m.channel == message.channel
            status = await client.wait_for('message', check=avail, timeout=120.0)
            status = status.content.lower()
            if status == 'true':
                card.available = True
            elif status == 'false':
                card.available = False
            else:
                await message.channel.send('Incorrect option.')
                return
        elif option in GUIDING_LANDS:
            await message.channel.send('Enter guilding land level, or `cancel`')
            def check_levels(m):
                return m.author == message.author and m.channel == message.channel
            level = await client.wait_for('message', check=check_levels, timeout=120.0)
            level = level.content.lower()
            try:
                if level == 'cancel':
                    return
                elif int(level) >= 1 and int(level) <=7:
                    levels[option] = int(level)
                else:
                    await message.channel.send('Incorrect input! Exiting guild card creation..')
                    return
            except ValueError:
                await message.channel.send('Input is not a number! Exiting guild card creation..')

        elif option == 'cancel':
            await message.channel.send('Cancelled guild card updating.')
            return
        else:
            await message.channel.send('Incorrect option! Exiting..')
            return
        if card.display_name != message.author.display_name:
            card.display_name = message.author.display_name
        card.save()
        card.reload()
        await message.channel.send('Guild card updated!')
        await showcard(card)

    async def searchCards(gl_type):
        gl_type = gl_type.lower()
        if gl_type in GUIDING_LANDS:
            cards = Player.objects.get_cards(gl_type).all()
            if cards:
                for c in cards:
                    await showcard(c)
            else:
                await message.channel.send('Unable to find cards.')
        else:
            await message.channel.send('Invalid search.')



######## USER COMMANDS ###############

    if message.content.startswith('/addsession'):
        channel = client.get_channel(706521000640249927) #asian squad
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
                title = '{}'.format(session_title)
                session_id = '```fix\n{}```'.format(session)
                embed = discord.Embed(description='```yaml\n{}```'.format(title), color=0xf1c40f)
                embed.add_field(name='Session ID', value=session_id)
                embed.set_footer(text='Added on {}'.format(now))
                embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
                msg = await channel.send(embed=embed)
                cemoji = await message.guild.fetch_emoji(707541604508106818)  # custom emoji to mark session close
                await msg.add_reaction(cemoji)
                logger.info('{} added session "{}"'.format(message.author.display_name, session))
            else:
                await message.channel.send('{}, incorrect command syntax. Please use `/addsession` instead.'.format(message.author.mention), delete_after= 10.0)
                return
        except asyncio.TimeoutError:
            logger.info('{} timed out when creating new session.'.format(message.author.display_name))
            await message.channel.send('{} timed out when creating new session.'.format(message.author.display_name), delete_after=5.0)
            pass
        finally:
            try:    #attempt message cleanup
                await message.delete()
                await prompt_session_id.delete()
                await session_id_reply.delete()
                await prompt_session_title.delete()
                await session_title_reply.delete()
            except discord.errors.NotFound: #if message not found and unable to delete
                pass
            except UnboundLocalError:
                pass
            except AttributeError:
                pass

    elif message.content.startswith('/addlfg'):
        channel = message.channel
        await message.delete()
        event_button = await message.guild.fetch_emoji(707790768324083732)
        siege_button = await message.guild.fetch_emoji(707790900927135765)
        msg = await channel.send('Click the following buttons to post a LFG/schedule a siege.\n'
                                 '{} for event, {} for siege.'.format(event_button, siege_button), delete_after=60.0)
        await msg.add_reaction(event_button)
        await msg.add_reaction(siege_button)

    elif message.content.startswith('/card'):
        chnl = client.get_channel(711487177606955087)
        if message.channel.id == 711487177606955087:
            card = Player.objects(player_id=message.author.id).first()
            if card is None:
                await message.channel.send('Creating guild card')
                await add_card()
            else:
                await message.channel.send('Guild card exist. Updating guild card instead.')
                await updatecards(card)
        else:
            await message.channel.send('Invalid channel. This command can only be used in {}'.format(chnl.mention))

    elif message.content.startswith('/showcard'):
        user_search = message.content[10:]
        if len(user_search) == 0:
            card = Player.objects(player_id=message.author.id).first()
        else:
            searched_member = message.guild.get_member_named(user_search)
            card = Player.objects(player_id=searched_member.id).first()
        if card is None and len(user_search) > 0:
            await message.channel.send('{}, guild card for {} not found. '.format(message.author.mention, user_search))
        elif card is None:
            await message.channel.send('{}, guild card not found. Type `/card` to create guild card.'.format(message.author.mention))
        else:
            await showcard(card)

    elif message.content.startswith('/searchcard'):
        land = message.content[12:]
        if land == '':
            await message.channel.send('Command is `/searchcard <guilding land>` \ne.g: `/searchcard forest`')
            return
        await searchCards(land)

    elif message.content.startswith('/help'):
        content = 'Available commands are: \n' \
                  '`/addsession <session_id>` - Adds a session with the given session ID \n' \
                  '`/addsession` - Bot will prompt you on what is the session ID \n' \
                  '`/addlfg` - Schedule an event or siege \n' \
                  '`/card` - Create a personal guild card \n' \
                  '`/showcard` - Show your guild card \n' \
                  '`/showcard hunter` - Show guild card for hunter \n' \
                  '`/searchcard forest` - Show all available guild card that has forest guilding lands leveled more than 6 \n' \
                  '`/help` - This help message.'
        await message.channel.send(content)

###### test command #####

    # elif message.content.startswith('!test'):
    #     me = message.author
    #     chnl = client.get_channel(716562012158689320)
    #     await chnl.set_permissions(me, read_messages=True, send_messages=True, embed_links=True)
    #     overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), me: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
        # new_chnl = await guild.create_text_channel('test', overwrites=overwrites)
        # await message.channel.send('Created new channel in {}'.format(new_chnl.mention))

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
            except asyncio.TimeoutError:
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

    elif message.content.startswith('&mute'):
        member_list = message.mentions
        for member in member_list:
            await member.edit(mute=True, reason='Muted by {}'.format(message.author.display_name))
            await message.channel.send('{} muted by {}'.format(member.display_name, message.author.display_name))

@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    channel_id = payload.channel_id
    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    guild = message.guild
    user = client.get_user(payload.user_id)
    bot_added_reactions = message.reactions #reactions that was added by bot in message
    if payload.emoji.is_custom_emoji() is True: #if user add emoji is custom
        emoji_add = payload.emoji.id  #set emoji_add to emoji id
    else:
        emoji_add = payload.emoji.name #else set to emoji name
    list_of_reactions = []

    if client.user.id == payload.user_id:
        return

    for reaction in bot_added_reactions:
        if reaction.me:
            try:
                list_of_reactions.append(reaction.emoji.id) #if can get emoji id means custom emoji
            except AttributeError:
                list_of_reactions.append(reaction.emoji) #if not is unicode emoji

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
            lfg_type = 'event'
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
                    event_time.content = '{} to contact participants.'.format(member.mention)
                await addlfg(message=message, lfg_type=lfg_type,description=event_title.content,member=member, time=event_time.content)
            except asyncio.TimeoutError:
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
            lfg_type = 'siege'
            member = payload.member

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
                    siege_time.content = '{} to contact participants.'.format(member.mention)

                await addlfg(message, lfg_type=lfg_type, description=siege_monster,member=member,time=siege_time.content)
            except asyncio.TimeoutError:
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
            member = payload.member
            post = Lfg.objects(message_id=payload.message_id).first()
            list_of_confirm = post.confirmed
            list_of_tentative = post.tentative
            embed = message.embeds[0]

            if post is None:
                return
            if member.id not in list_of_confirm:
                if (len(list_of_confirm) >=4 and post.lfg_type == 'event') or (len(list_of_confirm) >=16 and post.lfg_type == 'siege'):
                    await message.channel.send('{}, Apologies, but party is full. Kindly register your interest as tentative instead.'.format(member.mention), delete_after=5.0)
                    try:
                        await message.remove_reaction('👍', member)
                    except discord.errors.HTTPException:
                        pass
                    return
                list_of_confirm.append(member.id)   #add player into confirmed list
                if member.id in list_of_tentative:
                    list_of_tentative.remove(member.id)
                confirm_name = []
                tentative_name = []
                for i in list_of_confirm:   #generate confirmed players list
                    m = guild.get_member(i)
                    confirm_name.append(m.display_name)
                for id in list_of_tentative:    #generate tentative players list
                    m = guild.get_member(id)
                    tentative_name.append(m.display_name)
                confirmed_players = '\n'.join(confirm_name)
                no_of_confirm = len(list_of_confirm)
                tentative_players = '\n'.join(tentative_name)
                no_of_tentative = len(list_of_tentative)
                if no_of_tentative == 0:
                    tentative_players = '--'
                embed.set_field_at(1, name='Confirmed: {}'.format(no_of_confirm), value=confirmed_players, inline=True)
                embed.set_field_at(2, name='Tentative: {}'.format(no_of_tentative), value=tentative_players, inline=True)
                await message.edit(embed=embed)
                post.confirmed = list_of_confirm
                post.tentative = list_of_tentative
                post.save()
                try:
                    await message.remove_reaction('❔', member)
                except discord.errors.HTTPException:
                    pass

        elif emoji_add == 707541604508106818:   #mark session closed :fail:
            embed = message.embeds[0]
            cemoji = await message.guild.fetch_emoji(707541604508106818)
            session = embed.fields[0].value
            session_id = re.findall("```fix\s([\w\W]+)```", session)[0]
            author = embed.author
            mod_logs_channel = guild.get_channel(711165655939809291)
            if author == payload.member.display_name or await check_mod(message.guild, payload.member, baseline=706481118152491061) is True:    #baseline set as veteran
                await channel.send('Session ID deleted by {}..'.format(payload.member.mention), delete_after=5.0)
                print(session_id)
                await message.delete()
                logger.info('Session ID {} deleted by {}'.format(session_id, payload.member.display_name))
            else:
                await channel.send('{}, thank you for informing that the session is closed. \nMods will verify and close if neccessary.'.format(payload.member.mention),delete_after=10.0)
                await message.remove_reaction(cemoji, payload.member)
                embed = discord.Embed(description='```fix\nA session is reported as closed!\n```', color=discord.Color.gold())
                embed.add_field(name='Session ID', value=session_id)
                embed.add_field(name='Reported message', value='[Jump to message]({})'.format(message.jump_url))
                embed.set_footer(text='Reported by {}'.format(payload.member.display_name), icon_url=payload.member.avatar_url)
                msg = await mod_logs_channel.send(embed=embed)
                await msg.add_reaction('💫')
                logger.info('{} attempted to delete session ID'.format(payload.member.name))

        elif emoji_add == '❌':
            member = payload.member
            post = Lfg.objects(message_id = payload.message_id).first()
            if post is None:
                return
            host_id = post.confirmed[0]
            host = client.get_user(host_id)
            if member.id == host_id:
                await channel.send('Post deleted..', delete_after=5.0)
                await message.delete()
                post.delete()
            else:
                await channel.send('{}, post can only be deleted by the {}.'.format(member.mention,host.mention), delete_after=5.0)
                await message.remove_reaction('❌', payload.member)

        elif emoji_add == '🚧':
            member = payload.member
            embed = message.embeds[0]
            post = Lfg.objects(message_id=message_id).first()
            host = post.confirmed[0]
            dm_channel = member.dm_channel
            if dm_channel is None:
                dm_channel = await member.create_dm()
            if member.id == host:
                try:
                    await message.channel.send('{}, a PM has been sent to you to update your post.'.format(member.mention), delete_after=5.0)
                    await dm_channel.send('What is the updated message? (Type `NA` to skip, `cancel` to quit)')
                    def check_desc(m):
                        return m.author == member and m.channel == dm_channel

                    new_description = await client.wait_for('message', check=check_desc, timeout=120.0)
                    if new_description.content.lower() == 'na':
                        description = None
                    elif new_description.content == 'cancel':
                        return
                    else:
                        description = new_description.content

                    await dm_channel.send('What is the new time? (Type `NA` to skip, `cancel` to quit)')
                    def check_time(m):
                        return m.author == member and m.channel == dm_channel
                    new_time = await client.wait_for('message', check=check_time, timeout=120.0)

                    if new_time.content.lower() == 'na':
                        time = None
                    elif new_time.content.lower() == 'cancel':
                        return
                    else:
                        time = new_time.content

                    if description is not None:
                        embed.description = '```fix\n{}\n```'.format(description)
                    if time is not None:
                        embed.set_field_at(0, name='Time:', value=time, inline=False)
                    if description is not None or time is not None:
                        await message.edit(embed=embed)
                        await dm_channel.send('Post updated in {}.'.format(message.channel.mention))
                except asyncio.TimeoutError:
                    await dm_channel.send('Updating of post timed out. Please try again.', delete_after=5.0)
                    logging.info('{} timed out when updating post.'.format(member.name))
                    pass
                finally:
                    try:
                        await message.remove_reaction('🚧', member)
                    except discord.errors.NotFound:
                        pass
                    except UnboundLocalError:
                        pass
            else:
                await channel.send('{}, post can only be edited by the 1st hunter in the list.'.format(member.mention),
                                   delete_after=5.0)
                await message.remove_reaction('🚧', member)

        elif emoji_add == '❔':
            member = payload.member
            embed = message.embeds[0]
            post = Lfg.objects(message_id=payload.message_id).first()
            list_of_tentative = post.tentative
            if post is None:
                return
            if len(post.confirmed) <=1 and member.id == post.confirmed[0]: #make sure theres at least 1 player in confirmed
                await message.remove_reaction('❔', member)
                return

            if member.id not in list_of_tentative:
                list_of_confirm = post.confirmed
                if member.id in list_of_confirm:
                    list_of_confirm.remove(member.id)   #remove player from confirmed list
                list_of_tentative.append(member.id) #add player to tentative list
                confirm_list = []
                tentative_list = []
                for id in list_of_confirm:  #generate players in confirm list for output
                    m = guild.get_member(id)
                    confirm_list.append(m.display_name)
                for id in list_of_tentative:  #generate tentative players list for output
                    m = guild.get_member(id)
                    tentative_list.append(m.display_name)
                no_of_tentative = len(tentative_list)   #get number of tentative
                no_of_confirm = len(confirm_list)   #get number of confirm
                tentative_players = '\n'.join(tentative_list)
                confirm_players = '\n'.join(confirm_list)
                embed.set_field_at(1,name='Confirmed: {}'.format(no_of_confirm), value=confirm_players, inline=True)
                embed.set_field_at(2, name='Tentative: {}'.format(no_of_tentative), value=tentative_players, inline=True)
                await message.edit(embed=embed)
                post.tentative = list_of_tentative
                post.confirmed = list_of_confirm
                post.save()
                try:
                    await message.remove_reaction('👍', member)
                except discord.errors.HTTPException:
                    pass
        elif emoji_add == '💫':
            await message.delete()
            await message.channel.send('Reported log resolved by {}..'.format(payload.member.mention), delete_after=5.0)
            logger.info('Log resolved by {}..'.format(payload.member.display_name))

@client.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    channel_id = payload.channel_id
    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    guild = message.guild
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
                embed = message.embeds[0]
                post = Lfg.objects(message_id=message_id).first()
                if post is None:
                    return
                list_of_players = post.confirmed
                if payload.user_id in list_of_players:
                    list_of_players.remove(payload.user_id)
                    player_list = []
                    for id in list_of_players:
                        member = guild.get_member(id)
                        player_list.append(member.display_name)
                    new_players = ('\n').join(player_list)
                    no_of_players = len(player_list)
                    embed.set_field_at(1, name='Confirmed: {}'.format(no_of_players), value=new_players, inline=True)
                    await message.edit(embed=embed)
                    post.confirmed = list_of_players
                    post.save()
            except discord.errors.HTTPException:
                pass

        elif emoji_remove == '❔':
            try:
                embed = message.embeds[0]
                post = Lfg.objects(message_id=message_id).first()
                if post is None:
                    return
                list_of_tentative = post.tentative
                if payload.user_id in list_of_tentative:
                    list_of_tentative.remove(payload.user_id)
                    tentative_list = []
                    for id in list_of_tentative:
                        member = guild.get_member(id)
                        tentative_list.append(member.display_name)
                    tentative_players = ('\n').join(tentative_list)
                    no_of_tentative = len(tentative_list)
                    if no_of_tentative == 0:
                        tentative_players = '--'
                    embed.set_field_at(2, name='Tentative: {}'.format(no_of_tentative), value=tentative_players, inline=True)
                    await message.edit(embed=embed)
                    post.tentative = list_of_tentative
                    post.save()
            except discord.errors.HTTPException:
                pass

@client.event
async def on_member_join(member):
    guild = client.get_guild(706463594719608883)
    new_fiver = guild.get_role(706870296334041088)
    newcomer = member.mention
    channel = client.get_channel(706463594719608886)
    general_channel = client.get_channel(706466658373599253)
    session_id_channel = client.get_channel(706521000640249927)
    read_first_channel = client.get_channel(706477462183346277)
    welcome_list = ["Keep your palicoes! {} is here to hunt!!".format(newcomer),
                    "{} is here to slay some Great Jagras!".format(newcomer),
                    "Here comes {}, the Rajang(ahem Rajunk) slayer!".format(newcomer),
                    "Welcome {} to the Gathering Hall.".format(newcomer),
                    "Thank the Elder dragons. {} is here to save us from Safi'jiiva!".format(newcomer),
                    "🐋 cum {} to the hunting hall.".format(newcomer),
                    "{} is here to cook us some raw meat.".format(newcomer)]
    index = random.randrange(0, len(welcome_list), 1)
    await channel.send('{}\nMake sure to read {}, drop by {} to say hi, and join our squad sessions at {}'.format(welcome_list[index],read_first_channel.mention, general_channel.mention, session_id_channel.mention))
    await member.add_roles(new_fiver)

# run discord bot
client.run(Config.discord_token)