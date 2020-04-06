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
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import MessageEntity, InlineKeyboardMarkup,InlineKeyboardButton
import praw
from config import Config
from datetime import datetime

logging.basicConfig(level=logging.INFO, filename='output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.info("Bot started succesfully.")
api_key = Config.API_KEY
#yt = YoutubeDataApi(api_key)

reddit = praw.Reddit(user_agent="MHW-Squaddie Telegram Bot (by /u/lonerzboy)", client_id=Config.client_id, client_secret=Config.client_secret)
logging.info("PRAW instantiated successfully.")

db = connect('sg', host=Config.host)
TOKEN = Config.token



class Player(Document):
    username = StringField(max_length=200, required=False)
    player_name = StringField(max_length=200, required=False)
    user_id = IntField(required=False)

class Siege(Document):
    siege_id = IntField(min_value=1, required=True)
    time = StringField(max_length=200, required=True)
    rounds = IntField(required=False)
    players = ListField(ReferenceField(Player))
    host = StringField(max_length=200, required=True)

class NewPlayer(Document):
    first_name = StringField(max_length=200, required = False)

class Session(Document):
    session_id = StringField(max_length=200, required = True)

class Event(Document):
    event_id = IntField(min_value=1, required=True)
    time = StringField(max_length=200, required=True)
    description = StringField(required=False)
    players = ListField(ReferenceField(Player))
    host = StringField(max_length=200, required=True)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def check_chat(id):
    if id == -1001336587845:
        return True
    else:
        return False
    # return True

def siegestatus():
    msg = []
    if Siege.objects.count() > 0:
        for siege in Siege.objects:
            index = 1
            siege_id = siege.siege_id

            player_list = siege.players
            players = []
            if len(player_list) > 0:
                for player in player_list:
                    username = player.username
                    player_name = player.player_name
                    message = "{}. {} ({})".format(index, username, player_name)
                    players.append(message)
                    if (index % 4) == 0:
                        players.append("")
                    index += 1
                players_message = "\n".join(players)
                msg_send = "<b>Siege ID:</b> {} \n<b>Siege time:</b> {} (GMT +8) \n<b>Started By:</b> {} \n<b>Players:</b> {} \n{}".format(siege_id, siege.time, siege.host, len(player_list),players_message)
                msg.append(msg_send)
            else:
                msg_send = "<b>Siege ID:</b> {} \n<b>Siege time:</b> {} (GMT +8) \n<b>Players:</b> 0 \nNo players in siege.".format(siege.siege_id, siege.time)
                msg.append(msg_send)
            msg.append("")
    else:
        msg_send = "No siege scheduled."
        msg.append(msg_send)
    message = "\n".join(msg)
    return message

def eventstatus():
    msg = []
    if Event.objects.count() > 0:
        event_list=[]
        for event in Event.objects:
            event_id = event.event_id
            event_list.append(event_id)
            event_list.sort()

        for i in event_list:
            event = Event.objects(event_id=i)[0]
            player_list = event.players
            players = []
            index = 1
            if len(player_list) > 0:
                for player in player_list:
                    username = player.username
                    player_name = player.player_name
                    message = "{}. {} ({})".format(index, username, player_name)
                    players.append(message)
                    index += 1
                players_message = "\n".join(players)
                msg_send = "<b>Event ID:</b> {} \n<b>Description: </b>{} \n<b>Event time:</b> {} (GMT +8) \n<b>Started By:</b> {} \n<b>Players:</b> {} \n{}".format(event.event_id, event.description ,event.time, event.host, len(player_list),players_message)
                msg.append(msg_send)
            else:
                msg_send = "<b>Event ID:</b> {} \n<b>Description: </b>{} \n<b>Event time:</b> {} (GMT +8) \n<b>Players:</b> 0 \nNo players in siege.".format(event.event_id, event.description,event.time)
                msg.append(msg_send)
            msg.append("")
    else:
        msg_send = "No event planned."
        msg.append(msg_send)
    message = "\n".join(msg)
    return message

def setsiege(update, context):
    if check_chat(update.message.chat.id):
        username = update.message.from_user.username
        player_name = update.message.from_user.first_name
        if username is None:
            update.message.reply_text("Kindly create a Telegram username first before joining siege.")
            return
        else:
            if not Player.objects(username=username):
                user = Player(username=username, player_name=player_name)
                user.save()
            else:
                user = Player.objects(username=username)[0]
        if len(context.args) == 0:
            update.message.reply_text('Command syntax is /setsiege <time>')
            return
        try:
            if '.' in context.args[0]:
                time_in_datetime = datetime.strptime(context.args[0], '%I.%M%p')
                time = time_in_datetime.strftime('%I.%M%p').lstrip('0')
            else:
                time_in_datetime = datetime.strptime(context.args[0], '%I%p')
                time = time_in_datetime.strftime('%I%p').lstrip('0')
        except ValueError:
            update.message.reply_text('Invalid time format. Syntax is /setsiege <time>')
            return
        if Siege.objects.count() == 0:
            siege_id = 1
        else:
            siege_id_list = []
            start_count =1
            for siege in Siege.objects():
                siege_id_list.append(siege.siege_id)
            siege_id_list.sort()
            for i in siege_id_list:
                if start_count == i: #already exist
                    start_count +=1
                else:
                    siege_id = start_count
            if start_count > len(siege_id_list):
                siege_id = start_count


        #siege_id = Siege.objects.count() + 1
        siege = Siege(siege_id=siege_id, time=time, players=[user], host=player_name)
        siege.save()
        update.message.reply_html('Siege scheduled at <b>{}</b>. \n Use /joinsiege to indicate your interest!'.format(time))
        db.close()

def joinsiege(update, context):
    if check_chat(update.message.chat.id):
        username = update.message.from_user.username
        player_name = update.message.from_user.first_name
        if username is None:
            update.message.reply_text("Kindly create a Telegram username first before joining siege.")
            return
        else:
            if not Player.objects(username=username):
                user = Player(username=username, player_name=player_name)
                user.save()
            else:
                user = Player.objects(username=username)[0]
        if Siege.objects.count() > 0:
            if len(context.args) == 0:
                id_join = 1
            else:
                id_join = int(context.args[0])
            if not Siege.objects(siege_id=id_join):
                if id_join == 1:
                    update.message.reply_text("Siege 1 is not active. \nPlease select siege ID to join.")
                else:
                    update.message.reply_text("Invalid siege ID")
                db.close()
                return
            siege = Siege.objects(siege_id=id_join)[0]
            player_list = siege.players
            for players in player_list:
                if players.username == username:
                    update.message.reply_html("Already in siege. Type /checksiege for siege status.")
                    return
            Siege.objects(siege_id=id_join).update_one(push__players=user)
            update.message.reply_html(siegestatus())
        else:
            update.reply_text("No siege scheduled.")

        db.close()

def leavesiege(update, context):
    if check_chat(update.message.chat.id):
        if Siege.objects.count() > 0:

            username = update.message.from_user.username
            player_name = update.message.from_user.first_name
            if username is None:
                update.message.reply_text("Kindly create a Telegram username first before joining siege.")
                return
            else:
                if not Player.objects(username=username):
                    user = Player(username=username, player_name=player_name)
                    user.save()
                else:
                    user = Player.objects(username=username)[0]
            if len(context.args) == 0:
                id_leave = 1
            else:
                id_leave = int(context.args[0])
            if not Siege.objects(siege_id=id_leave):
                if id_leave == 1:
                    update.message.reply_text("Siege 1 is not active. \nPlease select siege ID to leave.")
                else:
                    update.message.reply_text("Invalid siege ID")
                db.close()
                return
            siege = Siege.objects(siege_id=id_leave)[0]
            player_list = siege.players
            for player in player_list:
                if player.username == username:
                    Siege.objects(siege_id=id_leave).update_one(pull__players=user)
                    update.message.reply_html("Left siege. \n\n{}".format(siegestatus()))
                    return
            update.message.reply_text("You are not in any siege.")
        else:
            update.message.reply_text("No siege scheduled")
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
            if len(context.args) == 0:
                to_delete = 1
            else:
                to_delete = int(context.args[0])
            if not Siege.objects(siege_id=to_delete):
                if to_delete == 1:
                    update.message.reply_text("Siege 1 is not active. \nPlease select siege ID to delete.")
                else:
                    update.message.reply_text("Invalid siege ID")
                db.close()
                return
            siege = Siege.objects(siege_id=to_delete)[0]
            siege.delete()
            update.message.reply_html('Siege ID <b>{}</b> deleted. Type /setsiege to schedule a new siege.'.format(to_delete))
        else:
            update.message.reply_text("No siege to delete.")
        db.close()


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

####Events######

def addevent(update, context):
    if check_chat(update.message.chat.id):
        username = update.message.from_user.username
        player_name = update.message.from_user.first_name
        if username is None:
            update.message.reply_text("Kindly create a Telegram username first before joining event.")
            return
        else:
            if not Player.objects(username=username):
                user = Player(username=username, player_name=player_name)
                user.save()
            else:
                user = Player.objects(username=username)[0]
        if len(context.args) == 0:
            update.message.reply_text('Command syntax is /addevent <time>,<description')
            return
        space_index = update.message.text.find(" ") #get the index after command
        input_message = update.message.text[space_index+1:] #the message we interested in
        time = input_message.split(',')[0].strip() #the first part of the message which is time
        message = input_message.split(',') #number of elements in the message
        if "," in time:
            time = time.replace(",", "")

        if len(message) < 2:
            update.message.reply_text('Missing time or description. \nCommand syntax is /addevent <time>,<description>')
            return
        try:
            if '.' in time:
                time_in_datetime = datetime.strptime(time, '%I.%M%p')
                time = time_in_datetime.strftime('%I.%M%p').lstrip('0')
            else:
                time_in_datetime = datetime.strptime(time, '%I%p')
                time = time_in_datetime.strftime('%I%p').lstrip('0')
        except ValueError:
            update.message.reply_text('Invalid time format. Syntax is /addevent <time>,<description>')
            return
        second_part_msg_index = input_message.find(',')
        description = input_message[second_part_msg_index+1:]
        if Event.objects.count() == 0:
            event_id = 1
        else:
            event_id_list = []
            start_count =1
            for event in Event.objects():
                event_id_list.append(event.event_id)
            event_id_list.sort()
            for i in event_id_list:
                if start_count == i: #already exist
                    start_count +=1
                else:
                    event_id = start_count
            if start_count > len(event_id_list):
                event_id = start_count


        event = Event(event_id=event_id, time=time,description=description, players=[user], host=player_name)
        event.save()
        update.message.reply_html('Event created at <b>{}</b>. \n Use /joinevent to indicate your interest!'.format(time))
        db.close()

def joinevent(update, context):
    if check_chat(update.message.chat.id):
        username = update.message.from_user.username
        player_name = update.message.from_user.first_name
        if username is None:
            update.message.reply_text("Kindly create a Telegram username first before joining siege.")
            return
        else:
            if not Player.objects(username=username):
                user = Player(username=username, player_name=player_name)
                user.save()
            else:
                user = Player.objects(username=username)[0]
        if Event.objects.count() > 0:
            if len(context.args) == 0:
                id_join = 1
            else:
                id_join = int(context.args[0])
            if not Event.objects(event_id=id_join):
                if id_join == 1:
                    update.message.reply_text("Event 1 is not active. \nPlease select event ID to join.")
                else:
                    update.message.reply_text("Invalid event ID")
                db.close()
                return
            event = Event.objects(event_id=id_join)[0]
            player_list = event.players
            for players in player_list:
                if players.username == username:
                    update.message.reply_html("Already in event. Type /checkevent for event status.")
                    return
            if len(player_list) >= 4:
                update.message.reply_html("Max number of players(4) already in event.")
            Event.objects(event_id=id_join).update_one(push__players=user)
            update.message.reply_html(eventstatus())
        else:
            update.reply_text("No event created.")

        db.close()

def deleteevent(update,context):
    if check_chat(update.message.chat.id):
        if Event.objects.count() > 0:
            if len(context.args) == 0:
                to_delete = 1
            else:
                to_delete = int(context.args[0])
            if not Event.objects(event_id=to_delete):
                if to_delete == 1:
                    update.message.reply_text("Event 1 is not active. \nPlease select event ID to delete.")
                else:
                    update.message.reply_text("Invalid event ID")
                db.close()
                return
            event = Event.objects(event_id=to_delete)[0]
            event.delete()
            update.message.reply_html('Event ID <b>{}</b> deleted. Type /addevent to plan a new event.'.format(to_delete))
        else:
            update.message.reply_text("No event to delete.")
        db.close()

def leaveevent(update, context):
    if check_chat(update.message.chat.id):
        if Event.objects.count() > 0:

            username = update.message.from_user.username
            player_name = update.message.from_user.first_name
            if username is None:
                update.message.reply_text("Kindly create a Telegram username first before joining siege.")
                return
            else:
                if not Player.objects(username=username):
                    user = Player(username=username, player_name=player_name)
                    user.save()
                else:
                    user = Player.objects(username=username)[0]
            if len(context.args) == 0:
                id_leave = 1
            else:
                id_leave = int(context.args[0])
            if not Event.objects(event_id=id_leave)[0]:
                if id_leave == 1:
                    update.message.reply_text("Event 1 is not active. \nPlease select event ID to leave.")
                else:
                    update.message.reply_text("Invalid event ID")
                db.close()
                return
            event = Event.objects(event_id=id_leave)[0]
            player_list = event.players
            for player in player_list:
                if player.username == username:
                    Event.objects(event_id=id_leave).update_one(pull__players=user)
                    update.message.reply_html("Left event. \n\n{}".format(eventstatus()))
                    return
            update.message.reply_text("You are not in any event.")
        else:
            update.message.reply_text("No event planned")
        db.close()

def checkevent(update, context):
    if check_chat(update.message.chat.id):
        if Event.objects.count() > 0:
            update.message.reply_html(eventstatus())
        else:
            update.message.reply_text("No event planned at the moment.")
        db.close()

def rules(update, context):
    if check_chat(update.message.chat.id):
        update.message.reply_html("Read the rules <a href='https://telegra.ph/Rules-and-Community-Guidelines-04-05'>here.</a>")

###### MEMBERS MANAGEMENT #######

def new_member(update,context):
    if check_chat(update.message.chat.id):
        for member in update.message.new_chat_members:
            newcomer = member.first_name
            keyboard = [[InlineKeyboardButton("Rules", url='https://telegra.ph/Rules-and-Community-Guidelines-04-05'),
                         InlineKeyboardButton("Squad Spreadsheet", url='https://docs.google.com/spreadsheets/d/1BOgecU-LdpHjZX_ruCRqoWgfzea-WTT9zYSnzmNzauA/edit#gid=0')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            welcome_list = ["Keep your palicoes! <b>{}</b> is here to hunt!!".format(newcomer),
                            "<b>{}</b> is here to slay some Great Jagras!".format(newcomer),
                            "Here comes <b>{}</b>, the Rajang(ahem Rajunk) slayer!".format(newcomer),
                            "Welcome <b>{}</b> to the Gathering Hall.".format(newcomer),
                            "Thank the Elder dragons. <b>{}</b> is here to save us from Safi'jiiva!".format(newcomer),
                            "<b>{}</b> is here to cook us some raw meat.".format(newcomer)]
            index = random.randrange(0,len(welcome_list),1)
            update.message.reply_html("{} \nMake sure to read the <b>rules</b> and add your PSN ID/IGN to the <b>squad spreadsheet</b> by using the buttons below.\n"
                                      "Tag @zacharylky or @bloodychaos for invitation to squad. Party up and have fun hunting!".format(welcome_list[index]), reply_markup=reply_markup)

def member_left(update,context):
    if check_chat(update.message.chat.id):
        member = update.message.left_chat_member
        first_name = member.first_name
        last_name = member.last_name
        name = first_name + ' ' + last_name
        byebye_list = ["Sadly, our comrade <b>{}</b> has left".format(name),
                        "Its..its not like I wanted <b>{}</b> to stay or anything!".format(name),
                        "<b>{}</b> has fallen to Rajang.".format(name)]
        index = random.randrange(0, len(byebye_list), 1)
        logging.info("{} had left the chat group.".format(name))
        update.message.reply_html("{}".format(byebye_list[index]))


####Session Management ####

def session(update, context):
    if check_chat(update.message.chat.id):
        if Session.objects.count() == 0:
            update.message.reply_text("No session created.")
        else:
            session_id = Session.objects[0].session_id
            update.message.reply_html("<b>Session ID:</b> {}".format(session_id))
            db.close()

def addsession(update, context):
    if check_chat(update.message.chat.id):
        if len(context.args) == 0:
            update.message.reply_text("Syntax is /addsession <session id>.")
            return
        if Session.objects.count() >= 1:
            update.message.reply_text("There is already an existing session. \n Join that instead.")
            return
        else:
            session_id = " ".join(context.args)
            print(session_id)
            session = Session(session_id=session_id)
            session.save()
            update.message.reply_html("<b>{}</b> added.".format(session_id))
            db.close()

def deletesession(update, context):
    if check_chat(update.message.chat.id):
        if Session.objects.count() == 0:
            update.message.reply_text("No session to delete.")
            db.close()
            return
        else:
            for session in Session.objects:
                session_id = session.session_id
                session.delete()
                update.message.reply_html("<b>{}</b> deleted.".format(session_id))
            db.close()

#Additional features

def reddit_link(update,context):
    text = update.message.text.split("/")
    if 'comments' in text and text.index('comments') > 0:
        submission_index = text.index('comments')+1
    else:
        return
    submission_id = text[submission_index]
    submission = reddit.submission(submission_id)
    if submission.selftext:
        submission_text = submission.selftext.split(" ")
        submission_reply = " ".join(submission_text[0:100])
        update.message.reply_html("<b>Summary(100 words):</b> \n\n{}".format(submission_reply))
    else:
        return


def googledocs(update,context):
    if check_chat(update.message.chat.id):
        update.message.reply_html('<a href="https://docs.google.com/spreadsheets/d/1BOgecU-LdpHjZX_ruCRqoWgfzea-WTT9zYSnzmNzauA/edit#gid=0">Google Spreadsheet Link</a>')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)
    logging.info("Waiting for commands..")

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
    dp.add_handler(CommandHandler('changetime', changetime))
    dp.add_handler(CommandHandler('session', session))
    dp.add_handler(CommandHandler('addsession', addsession))
    dp.add_handler(CommandHandler('deletesession', deletesession))
    dp.add_handler(CommandHandler('addevent', addevent))
    dp.add_handler(CommandHandler('joinevent', joinevent))
    dp.add_handler(CommandHandler('deleteevent', deleteevent))
    dp.add_handler(CommandHandler('checkevent', checkevent))
    dp.add_handler(CommandHandler('leaveevent', leaveevent))
    dp.add_handler(CommandHandler('googledocs', googledocs))
    dp.add_handler(CommandHandler('rules', rules))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))
    dp.add_handler(MessageHandler(Filters.text & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)),reddit_link))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, member_left))

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