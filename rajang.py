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
            session_id_reply = await client.wait_for('message', check=check_session_id)
            session = session_id_reply.content

            prompt_session_title = await message.channel.send('Any specific goals for the session? (Type cancel for general hunting)')
            def check_session_title(m):
                return m.channel == message.channel and m.author == message.author
            session_title_reply = await client.wait_for('message', check=check_session_title)

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
        embed = discord.Embed(title=title, color=0xf1c40f)
        embed.add_field(name='Session ID', value=session_id)
        embed.set_footer(text='Added on {}'.format(now))
        embed.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
        msg = await channel.send(embed=embed)
        await msg.add_reaction('🗑️')
        await message.delete()
        if prompt_session_id is not None:
            await prompt_session_id.delete()
            await session_id_reply.delete()
        if prompt_session_title is not None:
            await prompt_session_title.delete()
            await session_title_reply.delete()



    elif message.content.startswith('&announce') and message.author.id == 100118233276764160:
        content = 'Type /addsession in any chat to create session. \nReact to 🗑️ to mark a session as closed.'
        msg = await message.channel.send(content)
        await msg.pin()

    elif message.content.startswith('&getserverid') and message.author.id == 100118233276764160:
        for guild in client.guilds:
            print('{} - {}'.format(guild.name, guild.id))
        await message.delete()

    elif message.content.startswith('&getroles'):
        guild = message.guild
        print(guild.roles)
        await message.delete()

    elif message.content.startswith('&setrules') and message.author.id == 100118233276764160:
        channel = message.channel
        msg = await channel.fetch_message(706491925649424434)
        await msg.add_reaction('✅')
        await message.delete()

    elif message.content.startswith('&removerules'):
        channel = message.channel
        msg = await channel.fetch_message(706491925649424434)
        await msg.remove_reaction('✅', message.author)
        await message.delete()

@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    channel_id = payload.channel_id
    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    emoji_add = payload.emoji.name
    user = client.get_user(payload.user_id)
    bot_added_reactions = message.reactions
    list_of_reactions = []

    for reaction in bot_added_reactions:
        list_of_reactions.append(reaction.emoji)

    if message.author.id == user.id:
        return

    if emoji_add in list_of_reactions:
        if emoji_add == '🗑️':
            await channel.send('Session ID deleted..',delete_after=5.0)
            await message.delete()
        elif emoji_add == '✅' and message_id == 706491925649424434:
            rules_message = await channel.fetch_message(706491925649424434)
            member = payload.member
            guild = message.guild
            new_fiver = guild.get_role(706870296334041088)
            await member.remove_roles(new_fiver)
            await rules_message.remove_reaction('✅', member)


@client.event
async def on_member_join(member):
    guild = client.get_guild(706463594719608883)
    new_fiver = guild.get_role(706870296334041088)
    newcomer = member.name
    channel = client.get_channel(706463594719608886)
    general_channel = client.get_channel(706466658373599253)
    session_id_channel = client.get_channel(706521000640249927)
    read_first_channel = client.get_channel(706477462183346277)
    welcome_list = ["Keep your palicoes! **{}** is here to hunt!!".format(newcomer),
                    "**{}** is here to slay some Great Jagras!".format(newcomer),
                    "Here comes **{}**, the Rajang(ahem Rajunk) slayer!".format(newcomer),
                    "Welcome **{}** to the Gathering Hall.".format(newcomer),
                    "Thank the Elder dragons. **{}** is here to save us from Safi'jiiva!".format(newcomer),
                    "🐋 cum **{}** to the hunting hall.".format(newcomer),
                    "**{}** is here to cook us some raw meat.".format(newcomer)]
    index = random.randrange(0, len(welcome_list), 1)
    await channel.send('{}\nMake sure to read {}, drop by {} to say hi, and join our squad sessions at {}'.format(welcome_list[index],read_first_channel.mention, general_channel.mention, session_id_channel.mention))
    await member.add_roles(new_fiver)

# run discord bot
client.run(Config.discord_token)