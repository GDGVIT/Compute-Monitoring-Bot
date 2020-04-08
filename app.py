import logging
import os
import random
import sys

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from getting_compute_data import (
    getting_netdata_data, 
    plotting_cpu_vs_time,
    plotting_and_returning_image,
    preparing_ram_graph_data
    
)

from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

mode = os.getenv("mode")
token = os.getenv("token")

if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=token)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, token))
else:
    logger.error("No mode specified!")
    sys.exit(1)


intro_text = """ I am a compute monitoring bot v1.\n
I can perform some very basic functions like give you some basic updates about your system.\n
Currently, I can monitor your cpu, ram, i/o read-write speed\n

Currently, I only support following outputs,\n 
1) cpu load- /cpu,\n
2) ram usage - /ram \n
3) enter/change credentials - /enterDetails \n

Btw, I don't save credentials, so make sure to set your credentials before using 1 and 2
"""

extra = """
Currently, I only support following outputs,\n 
1) cpu load- /cpu,\n
2) ram usage - /ram \n

Please enter the following info in order to let us monitor you
"""


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=intro_text)
        
# def host_enter(update, context):
#     update.message.reply_text("Enter host")
#     host = update.message.text
    # update.message.reply_text("Enter username")
    # username = update.message.text
    # update.message.reply_text("Enter password")
    # password = update.message.text
    # print(username)
    # print(password)
    # print(host)


def cpu_usage(update, context):
    user_data = context.user_data
    output = user_data_check(user_data)
    if output:
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please wait until we try to probe this server to get a response")
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=plotting_cpu_vs_time(user_data['Host'], user_data['Username'], user_data['Password']))
def ram_usage(update, context):
    user_data = context.user_data
    output = user_data_check(user_data)
    if output:
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please wait until we try to probe this server to get a response")

        data = preparing_ram_graph_data(user_data['Host'], user_data['Username'], user_data['Password'])        
        free_ram = plotting_and_returning_image(data['time'], data['free_ram'], 'Free Ram', 'time')
        context.bot.send_message(chat_id=update.effective_chat.id, text='The following is an analysis of ram usage\n')
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=free_ram)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Free Ram Usage\n')
        
        used_ram = plotting_and_returning_image(data['time'], data['used_ram'], 'Used Ram', 'time')
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=used_ram)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Used Ram Usage\n')
        
        cached_ram = plotting_and_returning_image(data['time'], data['cached_ram'], 'Cached Ram', 'time')
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=cached_ram)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Cached Ram Usage\n')
        
        buffers_ram = plotting_and_returning_image(data['time'], data['buffers_ram'], 'Buffer Ram', 'time')
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=buffers_ram)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Buffer Ram Usage\n')


CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Host', 'Username', 'Password'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def user_data_check(user_data):
    if 'Host' not in user_data:
        return "Host not set. Use /enterDetails to set it."
    if 'Username' not in user_data:
        return "Username not set. Use /enterDetails to set it."
    if 'Password' not in user_data:
        return "Password not set. Use /enterDetails to set it."



def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))
    return "\n".join(facts).join(['\n', '\n'])


def startchoice(update, context):
    update.message.reply_text(extra,
        reply_markup=markup)

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Please enter your {}'.format(text))

    return TYPING_REPLY



def custom_choice(update, context):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "{} You can tell me more, or change your opinion"
                              " on something.".format(facts_to_str(user_data)),
                              reply_markup=markup)

    return CHOOSING


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "{}"
                              " Use these now to view the respective outputs \n 1) cpu load- /cpu,\n 2) ram usage - /ram \n".format(facts_to_str(user_data)))

    print(user_data)
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)




    

if __name__=='__main__':

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("cpu", cpu_usage))
    updater.dispatcher.add_handler(CommandHandler("ram", ram_usage))

    #updater.dispatcher.add_handler(MessageHandler(Filters.text, host_enter))
    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('enterDetails', startchoice)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Host|Username|Password)$'),
                                      regular_choice),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice)
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )
    )
    
    run(updater)
