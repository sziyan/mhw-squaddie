import discord
from config import Config
import logging
from mongoengine import *
from mongoengine import connect

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
        content = message.content[12:]
        if content == "":
            await message.channel.send('Please input session ID.')
        session = "".join(content.split())
        session = session[:4] + ' ' + session[4:8] + ' ' + session[8:12]
        description = '```fix\n{}```'.format(session)
        embed = discord.Embed(color=0xf1c40f)
        embed.add_field(name='Session ID', value=description)
        await message.delete()
        msg = await channel.send(embed=embed)
        await msg.add_reaction('🗑️')

    elif message.content.startswith('&announce'):
        content = 'Type /addsession in any chat to create session. \nReact to 🗑️ to mark a session as closed.'
        msg = await message.channel.send(content)
        await msg.pin()

    elif message.content.startswith('/channelid'):
        channel_id = message.channel.id
        print(channel_id)

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


# run discord bot
client.run(Config.discord_token)