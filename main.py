import logging
import time

import os

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
#from telegram.ext.dispatcher import run_async

from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


from helper_functions import (
    check_ip,
    probe_server
)

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


from getting_data_from_client import (
    get_available_choices_to_monitor_list,
    get_available_choices_to_monitor,
    respond_to_server_request
)




machine_set_up = """

Ok, so you chose to set up a new machine profile to monitor
We need the ip address of the machine to monitor.
Make sure that our client side tool exists on that server.

"""
ask_for_ip_address = """

Please enter your server IP address

"""
#check_server_health, ssh_check, stats_logging = [i for i in range(3)]

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="This is Vm monitor goto /setIp")

reply_keyboard = [['Set Ip Address', 'Change Ip Address'],
                  ['Exit']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def user_data_check(user_data):
    if 'Ip Address' not in user_data:
        return "Ip Address not set. Use /setIp to set it."


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))
    return "\n".join(facts).join(['\n', '\n'])


def start_ip_convo(update, context):
    update.message.reply_text("You chose to set up your Ip address",
        reply_markup=markup)

    return CHOOSING


def choice_for_read_or_update_ip(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        '{}'.format(text))

    return TYPING_REPLY


def storing_or_modifying_ip(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    
    if check_ip(text):
        update.message.reply_text("Your Ip Address is set to {}".format(text),reply_markup=markup)
        user_data['ip_address'] = text
        del user_data['choice']
    else:
        update.message.reply_text("You set up an improper Ip, Please change it.")
    
    return CHOOSING
    

def cancel(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    
    if 'ip_address' in user_data:
        update.message.reply_text("You Ip Address is currently set as {}".format(user_data['ip_address']))
    else:
        update.message.reply_text("You chose to cancel")
    #print(user_data)
    return ConversationHandler.END


def probe_server_from_bot(update, context):
    user_data = context.user_data
    if 'ip_address' not in user_data:
        update.message.reply_text("Your Ip address is not set. Set it up at /setIp")
    elif check_ip(user_data['ip_address']):
        ip_address = user_data['ip_address']
        if probe_server(ip_address):
            update.message.reply_text("Server is up and running")
        else:
            update.message.reply_text("Server seems down, Is the client side part working or is your server up ? Please check")
    else:
        update.message.reply_text("You set up an improper Ip, please setup a proper one")


# Working on monitoring data

# Need to hardcode this
keyboard_choices = get_available_choices_to_monitor_list()
monitor_reply_keyboard = [keyboard_choices[0:3],keyboard_choices[3:6],
keyboard_choices[6:], ['Exit']
]
monitor_markup = ReplyKeyboardMarkup(monitor_reply_keyboard, one_time_keyboard=True)


def start_monitoring(update, context):
    user_data = context.user_data
    if 'ip_address' not in user_data:
        update.message.reply_text("Ip not set. Please user /setIp to set the Ip of the system to monitor")    
    else:
        ip_address = user_data['ip_address']
        if check_ip(ip_address):
            update.message.reply_text("You chose to start monitoring system {}".format(ip_address),reply_markup=monitor_markup)
            return CHOOSING
        else:
            update.message.reply_text("You set up an improper Ip, please setup a proper one at /setIp")


def choice_for_choosing_which_factor_to_monitor(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text("Fetching details of your server.........")
    update.message.reply_text("Press 1 to see current stats only and 2 to see stats with graph")


    return TYPING_REPLY


def getting_data_for_choice_made_for_monitor(update, context):
    text = update.message.text
    if text == '1':
        update.message.reply_text("You chose current stats only")
    elif text == '2':
        update.message.reply_text("You chose stats with graph")
    
    user_data = context.user_data
    get_user_choice = user_data['choice']
    if get_user_choice in keyboard_choices:
        update.message.reply_text("You chose to see {}".format(get_user_choice))
    else:
        update.message.reply_text("Didnt understand your choice")

    del user_data['choice']

    update.message.reply_text("Select any other option to execute it",reply_markup=monitor_markup)

    return CHOOSING


def cancel_monitoring(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    
    update.message.reply_text("You chose to cancel")
    return ConversationHandler.END


# Creating a Scheduler to Get Data

scheduler_reply_keyboard = [['Name of the Event'],['Minute', 'Hour'], ['Day of Month'], ['Select A Month'], ['Exit']]
scheduler_markup = ReplyKeyboardMarkup(scheduler_reply_keyboard, one_time_keyboard=True)

def start_schedule_updates(update, context):
    user_data = context.user_data
    if 'ip_address' not in user_data:
        update.message.reply_text("Ip not set. Please user /setIp to set the Ip of the system to set up scheduled monitoring")    
    else:
        ip_address = user_data['ip_address']
        if check_ip(ip_address):
            update.message.reply_text("You chose to create a new scheduler for the system {}".format(ip_address),reply_markup=scheduler_markup)
            return CHOOSING
        else:
            update.message.reply_text("You set up an improper Ip, please setup a proper one at /setIp")


def choosing_schedule_parameters(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Please enter {}'.format(text))

    return TYPING_REPLY


def setting_up_scheduler_job(update, context):
    text = update.message.text
    user = update.message.from_user
    if text == '1':
        update.message.reply_text("You chose current stats only")
        update.message.reply_text("User Id is {}".format(user['id']))
    elif text == '2':
        update.message.reply_text("You chose stats with graph")
    
    user_data = context.user_data
    get_user_choice = user_data['choice']
    if get_user_choice in keyboard_choices:
        update.message.reply_text("You chose to see {}".format(get_user_choice))
    else:
        update.message.reply_text("Didnt understand your choice")

    del user_data['choice']

    update.message.reply_text("Select any other option to execute it",reply_markup=monitor_markup)

    return CHOOSING


def cancel_monitoring(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    
    update.message.reply_text("You chose to cancel")
    return ConversationHandler.END





if __name__=='__main__':

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("server_status", probe_server_from_bot))

    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('setIp', start_ip_convo)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Set Ip Address|Change Ip Address)$'),
                                      choice_for_read_or_update_ip),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           choice_for_read_or_update_ip)
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          storing_or_modifying_ip),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Exit$'), cancel)]
    )
    )



    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('monitor', start_monitoring)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^({})$'.format('|'.join(get_available_choices_to_monitor_list()))),
                                      choice_for_choosing_which_factor_to_monitor),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           choice_for_choosing_which_factor_to_monitor)
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          getting_data_for_choice_made_for_monitor),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Exit$'), cancel_monitoring)]
    )
    )
 
    run(updater)


