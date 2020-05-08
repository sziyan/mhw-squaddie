import discord
from config import Config
import logging
from mongoengine import *
from mongoengine import connect
import random
import datetime

client = discord.Client()
logging.basicConfig(level=logging.INFO, filename='discord_output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.info("Bot started succesfully.")

db = connect('sg', host=Config.host)
#mod_role_name = [The Asian Squad - GrandBotMaster, Ascenion - Admin]
MOD_ROLE_ID = [706468834235645954, 100920245190946816]

class Siege(Document):
    siege_id = IntField(min_value=1, required=True)
    time = StringField(max_length=200, required=True)
    rounds = IntField(required=False)
    players = ListField()
    host = StringField(max_length=200, required=True)

class Event(Document):
    event_id = IntField(min_value=1, required=True)
    time = StringField(max_length=200, required=True)
    description = StringField(required=False)
    players = ListField(IntField())
    host = StringField(max_length=200, required=True)

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

        content = message.content[12:]
        if content == "":
            prompt_session_id = await message.channel.send('Setting new session.. Whats the session ID?')
            def check_session_id(m):
                return m.channel == message.channel and m.author == message.author
            session_id_reply = await client.wait_for('message', check=check_session_id, timeout=30.0)
            session = session_id_reply.content

            prompt_session_title = await message.channel.send('Any specific goals for the session? (Type `cancel` for general hunting)')
            def check_session_title(m):
                return m.channel == message.channel and m.author == message.author
            session_title_reply = await client.wait_for('message', check=check_session_title, timeout=30.0)

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
        if prompt_session_id is not None:
            await prompt_session_id.delete()
            await session_id_reply.delete()
        if prompt_session_title is not None:
            await prompt_session_title.delete()
            await session_title_reply.delete()

    elif message.content.startswith('/help'):
        content = 'Available commands are: \n' \
                  '`/addsession <session_id>` - Adds a session with the given session ID \n' \
                  '`/addsession` - Bot will prompt you on what is the session ID \n' \
                  '`/help` - This help message.'
        await message.channel.send(content)

    # elif message.content.startswith('!test'):
    #     await message.channel.send(message.author.top_role.id)

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
            prompt_pin_message = await message.channel.send('What is the content of pinned message?', delete_after=30.0)
            def check_msg(m):
                return m.channel == message.channel and m.author == message.author
            pinned_message = await client.wait_for('message', check=check_msg, timeout=30.0)

            while ask_reaction is True:
                prompt_reaction = await message.channel.send('Send me a emoji for the reaction(type `cancel` to cancel reaction adding.)', delete_after=30.0)

                def check_emoji(m):
                    return m.channel == message.channel and m.author == message.author
                reaction_check = await client.wait_for('message', check=check_emoji, timeout=30.0)

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


    elif message.content.startswith('&getserverid') and message.author.id == 100118233276764160:
        member = message.author
        top_role = member.top_role
        if top_role.id not in MOD_ROLE_ID:
            return
        else:
            for guild in client.guilds:
                print('{} - {}'.format(guild.name, guild.id))
        await message.delete()

    elif message.content.startswith('&getroles'):
        member = message.author
        top_role = member.top_role
        if top_role.id not in MOD_ROLE_ID:
            return
        else:
            guild = message.guild
            print(guild.roles)
        await message.delete()

    elif message.content.startswith('&setrules') and message.author.id == 100118233276764160:
        channel = message.channel
        msg = await channel.fetch_message(706491925649424434)
        await msg.add_reaction('✅')
        await message.delete()

    # elif message.content.startswith('&removerules'):
    #     channel = message.channel
    #     msg = await channel.fetch_message(706491925649424434)
    #     await msg.remove_reaction('✅', message.author)
    #     await message.delete()

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
        try:
            list_of_reactions.append(reaction.emoji.id) #if can get emoji id means custom emoji
        except:
            list_of_reactions.append(reaction.emoji) #if not is unicode emoji

    if message.author.id == user.id:
        return

    if emoji_add in list_of_reactions:
        if emoji_add == '✅' and message_id == 706491925649424434:
            rules_message = await channel.fetch_message(706491925649424434)
            member = payload.member
            guild = message.guild
            new_fiver = guild.get_role(706870296334041088)
            await member.remove_roles(new_fiver)
            await rules_message.remove_reaction('✅', member)

        elif emoji_add == '⚔️':
            now = datetime.datetime.now().strftime('%d %b %I:%M %p')
            member = payload.member
            await message.remove_reaction(emoji_add, member)
            prompt_event_title = await message.channel.send('What is the name of event?', delete_after=30.0)
            def check_event(m):
                return m.author == member and m.channel == channel
            event_title = await client.wait_for('message', check=check_event, timeout=30.0)
            prompt_time = await message.channel.send('What time is the event?', delete_after=30.0)
            def check_time(m):
                return m.author == member and m.channel == message.channel
            event_time = await client.wait_for('message', check=check_time, timeout=30.0)
            event_title_description = '```fix\n{}\n```'.format(event_title.content)
            e = discord.Embed(title='Event!!',description=event_title_description)
            e.add_field(name='Time (GMT+8)', value=event_time.content, inline=False)
            e.add_field(name='Players', value=member.mention, inline=False)
            e.set_footer(text='Added on {}'.format(now))
            e.set_author(name=member.display_name, icon_url=member.avatar_url)
            msg = await message.channel.send(embed=e)
            await msg.add_reaction('👍')
            await msg.add_reaction('❌')
            await prompt_event_title.delete()
            await prompt_time.delete()
            await event_title.delete()
            await event_time.delete()

        elif emoji_add == '👍':
            member = payload.member.mention
            embed = message.embeds[0]
            fields = embed.fields
            players = fields[1].value
            list_of_players = players.split()
            if member not in list_of_players:
                list_of_players.append(member)
                new_players = '\n'.join(list_of_players)
                embed.set_field_at(1, name='Players', value=new_players, inline=False)
                await message.edit(embed=embed)

        elif emoji_add == 707541604508106818:
            await channel.send('Session ID deleted..', delete_after=5.0)
            await message.delete()

        elif emoji_add == '❌':
            member = payload.member.mention
            embed = message.embeds[0]
            fields = embed.fields
            players = fields[1].value
            host = players.split()[0]
            if member == host:
                await channel.send('Event deleted..', delete_after=5.0)
                await message.delete()
            else:
                await channel.send('{}, event can only be deleted by the 1st player in the player list.'.format(member), delete_after=5.0)
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
                member = user.mention
                embed = message.embeds[0]
                fields = embed.fields
                players = fields[1].value
                list_of_players = players.split()
                if member in list_of_players:
                    list_of_players.remove(member)
                    new_players = ('\n').join(list_of_players)
                    embed.set_field_at(1, name='Players', value=new_players, inline=False)
                    await message.edit(embed=embed)
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