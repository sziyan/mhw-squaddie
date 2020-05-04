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

class Session(Document):
    session_id = StringField(max_length=200, required = True)

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
        content = message.content[12:]
        if content == "":
            await message.channel.send('Please input session ID.')
        session = "".join(content.split())
        session = session[:4] + ' ' + session[4:8] + ' ' + session[8:12]
        description = '```fix\n{}```'.format(session)
        embed = discord.Embed(color=0xf1c40f)
        embed.add_field(name='Session ID', value=description)
        embed.set_footer(text='Created on {}'.format(now))
        await message.delete()
        msg = await channel.send(embed=embed)
        await msg.add_reaction('🗑️')

    elif message.content.startswith('&announce') and message.author.id == 100118233276764160:
        content = 'Type /addsession in any chat to create session. \nReact to 🗑️ to mark a session as closed.'
        msg = await message.channel.send(content)
        await msg.pin()


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

@client.event
async def on_member_join(member):
    newcomer = member.name
    channel = client.get_channel(706463594719608886)
    welcome_list = ["Keep your palicoes! **{}** is here to hunt!!".format(newcomer),
                    "**{}** is here to slay some Great Jagras!".format(newcomer),
                    "Here comes **{}**, the Rajang(ahem Rajunk) slayer!".format(newcomer),
                    "Welcome **{}** to the Gathering Hall.".format(newcomer),
                    "Thank the Elder dragons. **{}** is here to save us from Safi'jiiva!".format(newcomer),
                    "🐋 cum **{}** to the hunting hall.".format(newcomer),
                    "**{}** is here to cook us some raw meat.".format(newcomer)]
    index = random.randrange(0, len(welcome_list), 1)
    await channel.send('```yaml\n{}\n```'.format(welcome_list[index]))


# run discord bot
client.run(Config.discord_token)