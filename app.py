#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import random
import logging
from mongoengine import *
from mongoengine import connect

db = connect('sg', host="mongodb+srv://ndg:P%40ssw0rd@ndg-3djuk.gcp.mongodb.net/sg?retryWrites=true&w=majority")
#TOKEN = '976932675:AAHRy9-sEEvbEfP8krrI2PkWESJmQADh888' #MHW Squaddie
TOKEN = '180665590:AAGEXQVVWTzpou9TBekb8oq59cjz2Fxp_gY' #Ascension

class Player(Document):
    username = StringField(max_length=200, required=False)
    player_name = StringField(max_length=200, required=False)
    time = StringField(max_length=200, required=False)

class Siege(Document):
    time = StringField(max_length=200, required = True)
    host = StringField(max_length=200, required = False)

class NewPlayer(Document):
    first_name = StringField(max_length=200, required = False)

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def check_chat(id):
    # if id == -1001336587845:
    #     return True
    # else:
    #     return False
    return True

def siegestatus():
    if Siege.objects.count() > 0:
        siege = Siege.objects[0]
        time = siege.time
        players = []
        index = 1
        if Player.objects.count() > 0:
            for player in Player.objects:
                message = "{}. {} ({})".format(index, player.username, player.player_name)
                index += 1
                players.append(message)
            players_list = "\n".join(players)
            msg = "<b>Siege time:</b> {} (GMT +8) \n<b>Players:</b> {} \n{}".format(time, Player.objects.count(), players_list)
        else:
            msg = "No players in siege."
    else:
        msg = 'No siege scheduled at the moment.'
        db.close()
    return msg

# def start(update, context):
#     """Send a message when the command /start is issued."""
#     chat_id = update.message.chat.id
#     user_id = update.message.from_user.id
#     admin = updater.getChatMember(chat_id,user_id).status
#     update.message.reply_text(admin)


def help(update, context):
    """Send a message when the command /help is issued."""
    print(update.message.chat.id)
    update.message.reply_text('Help!')

def setsiege(update, context):
    if check_chat(update.message.chat.id):
        if len(context.args) == 0:
            update.message.reply_text('Command syntax is /setsiege <time>')
            return
        if Siege.objects.count() > 0:
            update.message.reply_text('There is already a scheduled siege. Use /checksiege or /joinsiege instead.')
        else:
            time = str((context.args[0]).upper())
            host = update.message.from_user.username
            player_name = update.message.from_user.first_name
            siege = Siege(time=time, host=host)
            siege.save()
            player = Player(username=host, time=time, player_name=player_name)
            player.save()
            update.message.reply_html('Siege scheduled at <b>{}</b>. \n Use /joinsiege to indicate your interest!'.format(time))
        db.close()

def joinsiege(update, context):
    if check_chat(update.message.chat.id):
        if Siege.objects.count() > 0:
            siege = Siege.objects[0]
            siege_time = siege.time
            player_username = update.message.from_user.username
            player_firstname = update.message.from_user.first_name
            if Player.objects.count() > 0: #at least 1 player in list
                for player in Player.objects:
                    if player_username is not None: #sender has username
                        if player.username == player_username: # sender already in list
                            update.message.reply_text("Already in siege. Type /checksiege for siege status.")
                            return
                        else: #sender not in list
                            player = Player(username=player_username,time=siege_time, player_name=update.message.from_user.first_name)
                            player.save()
                            update.message.reply_html(siegestatus())
                    else: #sender no username
                        if player_firstname == player.player_name: #sender already in list || check by firstname instead
                            update.message.reply_text("Already in siege.")
                            return
                        else: #sender not in list
                            player_name = update.message.from_user.first_name
                            player = Player(username=player_username, time=siege_time, player_name=player_name)
                            player.save()
                            update.message.reply_html(siegestatus())
            else: #no player object
                player_username = update.message.from_user.username
                player = Player(username=player_username, time=siege_time,player_name=update.message.from_user.first_name)
                player.save()
                update.message.reply_html(siegestatus())
        else: #no siege
            update.message.reply_text("No siege scheduled at the moment.")
        db.close()

def leavesiege(update, context):
    if check_chat(update.message.chat.id):
        if Siege.objects.count() > 0 and Player.objects.count() > 0:
            player_username = update.message.from_user.username
            player_name = update.message.from_user.first_name
            for player in Player.objects:
                if player.username is not None: #sender has username set
                    if player_username == player.username: #if found username
                        player.delete()
                        update.message.reply_html('Left the siege. \n{}'.format(siegestatus()))
                        db.close()
                        return
                    else: #cannot find username
                        update.message.reply_text('You are not in any siege.')
                else: #sender username not set
                    if player_name == player.player_name:
                        player.delete()
                        update.message.reply_html('Left the siege. \n{}'.format(siegestatus()))
                        db.close()
                        return
                    else:
                        update.message.reply_text('You are not in any siege.')
        else:
            update.message.reply_text('No siege scheduled.')
        db.close()

def checksiege(update, context):
    if check_chat(update.message.chat.id):
        if Siege.objects.count() > 0:
            update.message.reply_html(siegestatus())
        else:
            update.message.reply_text("No siege scheduled at the moment.")
        db.close()

def deletesiege(update,context):
    if check_chat(update.message.chat.id):
        if Siege.objects.count() > 0:
            siege = Siege.objects[0]
            siege.delete()
            if Player.objects.count() > 0:
                for player in Player.objects:
                    player.delete()
                update.message.reply_text('Siege deleted. Type /setsiege <time> to schedule a new siege.')
            update.message.reply_text("No players in siege to delete. Siege deleted.")
        else:
            update.message.reply_text("No siege to delete.")
        db.close()


# def echo(update, context):
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)

def changetime(update, context):
    if check_chat(update.message.chat.id):
        if len(context.args) == 0:
            update.message.reply_text("Syntax is /changetime <new time>.")
            return
        if Siege.objects.count() > 0:
            new_time = (context.args[0]).upper()
            siege = Siege.objects[0]
            siege.time = new_time
            siege.save()
            db.close()
            update.message.reply_html("Siege timing change to <b>{}</b>. \n{}".format(new_time, siegestatus()))
        else:
            update.message.reply_text("No siege scheduled at the moment. \nUse /setsiege <time> to schedule a siege.")

###### MEMBERS MANAGEMENT #######

def new_member(update,context):
    if check_chat(update.message.chat.id):
        for member in update.message.new_chat_members:
            newcomer = member.first_name
            newplayer = NewPlayer(first_name=newcomer)
            newplayer.save()
            welcome_list = ["Keep your palicoes! <b>{}</b> is here to hunt!!".format(newcomer),
                            "<b>{}</b> is here to slay some Great Jagras!".format(newcomer),
                            "Here comes <b>{}</b>, the Rajang sayer!".format(newcomer)]
            index = random.randrange(0,len(welcome_list),1)
            update.message.reply_html("{} \nP.S: Check the pinned message to add your IGN for others to add you.".format(welcome_list[index]))
            db.close()


def pendingsquad(update,context):
    if check_chat(update.message.chat.id):
        if NewPlayer.objects.count() > 0:
            new_players = []
            index = 1
            for member in NewPlayer.objects:
                message = "{}. {}".format(index, member.first_name)
                index += 1
                new_players.append(message)
            msg = "\n".join(new_players)
            update.message.reply_html("The following players just joined and is pending to be added to squad: \n{}".format(msg))
            db.close()
        else:
            update.message.reply_text("No pending members to join squad.")

def invitedsquad(update, context):
    if check_chat(update.message.chat.id):
        if NewPlayer.objects.count() > 0:
            if len(context.args) == 0:
                update.message.reply_text("Syntax is /invitedsquad <username>")
                return
            player_name = context.args[0]
            for member in NewPlayer.objects:
                if player_name == member.first_name:
                    update.message.reply_html("<b>{}</b> removed from list.".format(member.first_name))
                    member.delete()
                    db.close()
                    return
            update.message.reply_text("Username not found.")
        else:
            update.message.reply_text("No players in list to be added to squad.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('setsiege', setsiege))
    dp.add_handler(CommandHandler('joinsiege', joinsiege))
    dp.add_handler(CommandHandler('leavesiege', leavesiege))
    dp.add_handler(CommandHandler('checksiege', checksiege))
    dp.add_handler(CommandHandler('deletesiege', deletesiege))
    dp.add_handler(CommandHandler('pendingsquad', pendingsquad))
    dp.add_handler(CommandHandler('invitedsquad', invitedsquad))
    dp.add_handler(CommandHandler('changetime', changetime))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()