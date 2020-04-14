import logging
import os
import random
import sys
import json

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from getting_compute_data import (
    getting_netdata_data, 
    plotting_cpu_vs_time,
    plotting_and_returning_image,
    preparing_ram_graph_data
    
)

from getting_data_from_client import (
    get_available_choices_to_monitor,
    get_available_choices_to_monitor_list,
    respond_to_server_request
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


CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)



# intro_text = """ I am a compute monitoring bot v1.\n
# I can perform some very basic functions like give you some basic updates about your system.\n
# Currently, I can monitor your cpu, ram, i/o read-write speed\n

# Currently, I only support following outputs,\n 
# 1) cpu load- /cpu,\n
# 2) ram usage - /ram \n
# 3) enter/change credentials - /enterDetails \n

# Btw, I don't save credentials, so make sure to set your credentials before using 1 and 2
# """

# extra = """
# Currently, I only support following outputs,\n 
# 1) cpu load- /cpu,\n
# 2) ram usage - /ram \n

# Please enter the following info in order to let us monitor you
# """

intro_text = "I am a compute monitoring bot v1"
extra = "Please enter the following info in order to let us monitor you"

# Functions to handle the bot

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=intro_text)


def cpu_usage(update, context):
    user_data = context.user_data
    output = user_data_check(user_data)
    if output:
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please wait until we try to probe this server to get a response")
    
        cpu_data_output = plotting_cpu_vs_time(user_data['Host'], user_data['Username'], user_data['Password'])
        if 'error' in cpu_data_output:
            context.bot.send_message(chat_id=update.effective_chat.id, text=cpu_data_output['error'])    
        else:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=cpu_data_output)
        
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

def available_choices(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_available_choices_to_monitor())


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

    #print(user_data)
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)



monitor_choices = get_available_choices_to_monitor_list()
reply_keyboard_for_monitoring = [monitor_choices[:3],monitor_choices[3:6],monitor_choices[6:],['Done']]
markup_for_monitoring = ReplyKeyboardMarkup(reply_keyboard_for_monitoring, one_time_keyboard=True)


    # def facts_to_str(self, user_data):
    #     facts = list()

    #     for key, value in user_data.items():
    #         facts.append('{} - {}'.format(key, value))
    #     return "\n".join(facts).join(['\n', '\n'])


def startformonitoring(update, context):
    update.message.reply_text(extra,
        reply_markup=markup_for_monitoring)

    return CHOOSING


def regular_choice_for_monitoring(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Press 1 to see  current stats,\n or 2 to view all stats for last 10 mins for {}\n'.format(text))
    return TYPING_REPLY


def received_information_for_monitoring(update, context):
    user_data = context.user_data
    text = update.message.text
    
    if str(text) == '1':
        print("Performing current stats lookup only.....")
        response = respond_to_server_request(user_data['choice'])
        data = json.loads(response)
        if 'Partitions' in data:
            for i in data['Partitions']:
                update.message.reply_text(str(data['Partitions'][i]) ,reply_markup=markup_for_monitoring)
            update.message.reply_text("Total Data"+str(data['Total Read']) ,reply_markup=markup_for_monitoring)
            update.message.reply_text("Total Write"+str(data['Total Write']) ,reply_markup=markup_for_monitoring)
        else:
            update.message.reply_text(response ,reply_markup=markup_for_monitoring)
    elif str(text) == '2':
        print("Performing lookup for last 10 mins....")
    # category = user_data['choice']
    # user_data[category] = text
    # del user_data['choice']
    # print(user_data)
    

    return CHOOSING

def done_monitoring(update, context):
    update.message.reply_text("Thank you for using our service")










    

if __name__=='__main__':

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("cpu", cpu_usage))
    updater.dispatcher.add_handler(CommandHandler("ram", ram_usage))
    updater.dispatcher.add_handler(CommandHandler("choice", available_choices))
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

    text = "|".join(get_available_choices_to_monitor_list())
    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('enterWhatToMonitor', startformonitoring)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^({})$'.format(text)),
                                      regular_choice_for_monitoring),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice_for_monitoring)
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information_for_monitoring),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done_monitoring)]
    )
    )


    run(updater)
