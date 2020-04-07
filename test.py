from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import MessageEntity, Bot,ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging

logging.basicConfig(level=logging.INFO, filename='output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
bot = Bot(token='918929045:AAGfcxwoXBP1yg8C8t7wy9cx7V0vy9CrIsk')


EVENT, TIME = range(2)

def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))
    return '\n'.join(facts).join(['\n', '\n'])



def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def start_event(update, context):
    update.message.reply_text('Creating new event. What is the event name?')
    return EVENT


def event(update, context):
    print('test')
    event_name = update.message.text
    context.user_data['event'] = event_name
    print('Event name: {}'.format(update.message.text))
    update.message.reply_text('Now, what time shall the event be held at?')

    return TIME


def time(update, context):
    time = update.message.text
    user_data = context.user_data
    user_data['time'] = time
    user = update.message.from_user
    first_name = user.first_name
    update.message.reply_text('Event created as below: \n'
                              'Host: {} \n'
                              'Event name: {} \n'
                              'Time: {}'.format(first_name,user_data['event'], user_data['time']))

    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text('Event creation cancelled.')

    return ConversationHandler.END

def help(update, context):
    user = update.message.from_user
    print(type(user))

    update.message.reply_text(id)



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater('918929045:AAGfcxwoXBP1yg8C8t7wy9cx7V0vy9CrIsk', use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    #updater.dispatcher.add_handler(CommandHandler('start', start))
    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('sevent', start_event)],
        states={
            EVENT: [MessageHandler(Filters.text, event)],
            TIME: [MessageHandler(Filters.text, time)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # on noncommand i.e message - echo the message on Telegram


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