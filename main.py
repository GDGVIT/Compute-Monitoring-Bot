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
    probe_server,
    making_a_cron_job,
    deleting_a_cron_job,
    deleting_all_cron_jobs,
    getting_current_data_from_server
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

bot_start_message = """

Hey there, I am a Server Monitoring Bot.
I can do some basic functions like 
give you instant stats about your server.
In Order to function, make sure for 3 things:
1) Know the IP address of your server.
2) Have my server side tool set up and running
(To check if my server side tool is running properly:
    1) Set up IP first- /setIp
    2) Check if server is up and running- /server_status
)
3) Have Netdata Installed and working properly.

In the usage of this bot, I prefer markup keyboard,
please click the desired button, whenever the keyboard
pops up to get the desired input/output
"""

bot_start_message_extension = """

Now a few general instructions:
1) I fetch live data from 
my client side server - /monitor
(Instantenous Stats only)
2) I can set scheduled monitoring for ram and cpu - /create_schedule
3) I can delete a scheduled monitoring task 
by using the name you provided - /delete_schedule
4) I can delete all scheduled tasks - /delete_all
        
"""

bot_start_message_second_extension = """
Setting up a Scheduled Monitor

I mainly need a unique name and some info
based on which I will set up your scheduler.
For mode choose one of the following Integers:
1 -> Cpu Usage Monitor
2 -> Used Ram Usage Monitor
3 -> Free Ram Usage Monitor
4 -> Both Used and Free Ram(Separate Stats) Monitor

Please keep the following limits in mind:
Name of the event - A unique name that 
you can remember later
minute -> 0-59
hour -> 0-23
day_of_the_month -> 1-31
month -> 1-12

putting a value for each of these parameters 
means the event repeats after every x units
of that parameter. For example putting minute
as 1 puts gives you updates every minute
You can chain multiple params too.

"""







CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message_extension)
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message_second_extension)

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message_extension)
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message_second_extension)

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
    update.message.reply_text(machine_set_up,
        reply_markup=markup)

    return CHOOSING


def choice_for_read_or_update_ip(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'You chosse to {}. Please do the same properly'.format(text))

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
        update.message.reply_text("You chose to cancel.")
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

# Need to hardcode this(Done)

monitor_reply_keyboard = [['System Information','Virtual Memory Info'],['Boot Time','Cpu Info','Swap Memory'],
['Disk Info','Network Info'], ['Exit']
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
    user_data = context.user_data
    ip_address = user_data['ip_address']
    # context.user_data['choice'] = text
    update.message.reply_text("Fetching details of your server.........")
    if text == 'Cpu Info':
        output = getting_current_data_from_server(ip_address, 'Cpu Info')
        update.message.reply_text(output)
        update.message.reply_text("Choose another option to view different stats, or press Exit to exit",reply_markup=monitor_markup)
    elif text == 'Virtual Memory Info':
        output = getting_current_data_from_server(ip_address, 'Virtual Memory Info')
        update.message.reply_text(output)
        update.message.reply_text("Choose another option to view different stats, or press Exit to exit",reply_markup=monitor_markup)
    elif text == 'System Information':
        output = getting_current_data_from_server(ip_address, 'System Information')
        update.message.reply_text(output)
        update.message.reply_text("Choose another option to view different stats, or press Exit to exit",reply_markup=monitor_markup)
    elif text == 'Boot Time':
        output = getting_current_data_from_server(ip_address, 'Boot Time')
        update.message.reply_text(output)
        update.message.reply_text("Choose another option to view different stats, or press Exit to exit",reply_markup=monitor_markup)
    elif text == 'Swap Memory':
        output = getting_current_data_from_server(ip_address, 'Swap Memory')
        update.message.reply_text(output)
        update.message.reply_text("Choose another option to view different stats, or press Exit to exit",reply_markup=monitor_markup)
    elif text == 'Network Info':
        output = getting_current_data_from_server(ip_address, 'Network Info')
        update.message.reply_text(output)
        update.message.reply_text("Choose another option to view different stats, or press Exit to exit",reply_markup=monitor_markup)
    elif text == 'Disk Info':
        # output = getting_current_data_from_server(ip_address, 'Disk Info')
        # for i in output:
        #     update.message.reply_text(output)
        update.message.reply_text("We encountered some error in Disk Info")
        update.message.reply_text("Choose another option to view different stats, or press Exit to exit",reply_markup=monitor_markup)

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
    
    update.message.reply_text("You chose to exit. Thank you for using our service!")
    return ConversationHandler.END


# Creating a Scheduler to Get Data

scheduler_reply_keyboard = [['Name of the Event'],['Minute', 'Hour'], ['Day of Month'], ['Select A Month','Mode'], ['Confirm','Exit']]
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


def setting_up_scheduler_parameter_value(update, context):
    text = update.message.text
    user_data = context.user_data
    user_data[user_data['choice']] = text

    # Put checks for the values of params
    update.message.reply_text("You set {} as {}".format(
        user_data['choice'], user_data[user_data['choice']]),reply_markup=scheduler_markup)
    del user_data['choice']

    return CHOOSING


def checking_if_all_scheduler_options_present(context):
    user_data = context.user_data
    print(user_data)
    params = ['Name of the Event','Minute', 'Hour','Day of Month', 'Select A Month', 'Mode']
    for i in params:
        if i not in user_data:
            return False
    return True

def cancel_setting_scheduler(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    
    update.message.reply_text("You chose to cancel")
    return ConversationHandler.END

def confirm_setting_scheduler(update, context):
    user = update.message.from_user
    user_id = user['id']
    user_data = context.user_data
    ip_address = user_data['ip_address']

    # Put checks for the values of params
    params = {
        'Minute': user_data['Minute'],
        'Hour': user_data['Hour'],
        'Day of Month': user_data['Day of Month'],
        'Select A Month': user_data['Select A Month'],
        'Mode': user_data['Mode']
    }
    if len(set(params.values())) == 1:
        if '0' not in params.values():
            pass
        else:
            update.message.reply_text("Cannot confirm with all settings as 0", reply_markup=scheduler_markup)
            return CHOOSING
    else:
        for i in params:
            if params[i] == '0':
                user_data[i] = '*'
    
    if checking_if_all_scheduler_options_present(context):
        params = {
            'user_id': user_id,
            'file_name': 'cron_jobs.py',
            'name_of_job': user_data['Name of the Event'],
            'minute': user_data['Minute'],
            'hour': user_data['Hour'],
            'day_of_month': user_data['Day of Month'],
            'month': user_data['Select A Month'],
            'mode': user_data['Mode']
        }
        print(params)
        output = making_a_cron_job(ip_address,params)
        update.message.reply_text(output[1])
        return ConversationHandler.END
    else:
        update.message.reply_text("All Required Parameters not set", reply_keyboard=scheduler_markup)
        return CHOOSING
    

# Deleting scheduled monitoring

def start_deleting_scheduled_update(update, context):
    user_data = context.user_data
    if 'ip_address' not in user_data:
        update.message.reply_text("Ip not set. Please user /setIp to set the Ip of the system to delete scheduled monitoring")    
    else:
        ip_address = user_data['ip_address']
        if check_ip(ip_address):
            update.message.reply_text("You chose to delete a scheduler for the system {}. Please enter the name of the scheduler".format(ip_address))
            return CHOOSING
        else:
            update.message.reply_text("You set up an improper Ip, please setup a proper one at /setIp")


def deleting_scheduled_update(update, context):
    name = update.message.text+' #set by Bot'
    user_data = context.user_data
    ip_address = user_data['ip_address']
    output = deleting_a_cron_job(ip_address, name)
    update.message.reply_text(output[1])
    return ConversationHandler.END

def cancel_deleting_scheduler(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    
    update.message.reply_text("You chose to cancel")
    return ConversationHandler.END


# Deleting all scheduler
def deleting_all_scheduler(update, context):
    user_data = context.user_data
    if 'ip_address' not in user_data:
        update.message.reply_text("Ip not set. Please user /setIp to set the Ip of the system to delete all scheduled monitoring")    
    else:
        ip_address = user_data['ip_address']
        output = deleting_all_cron_jobs(ip_address)
        if output:
            update.message.reply_text("Successfully Deleted all Scheduled Monitors")
        else:
            update.message.reply_text("Error in  deleting all Scheduled Monitors")



if __name__=='__main__':

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("server_status", probe_server_from_bot))
    updater.dispatcher.add_handler(CommandHandler("help", help))
    # Conversation Handler for setting Ip
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


    # Conversation Handler for Monitoring
    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('monitor', start_monitoring)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(System Information|Boot Time|Cpu Info|Virtual Memory Info|Swap Memory|Disk Info|Network Info)$'),
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
    
    # Conversation Handler for Creating a scheduled Monitor
    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('create_schedule', start_schedule_updates)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Name of the Event|Minute|Hour|Day of Month|Select A Month|Mode)$'),
                                      choosing_schedule_parameters),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           choosing_schedule_parameters)
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          setting_up_scheduler_parameter_value),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Exit$'), cancel_monitoring),
        MessageHandler(Filters.regex('^Confirm$'), confirm_setting_scheduler),
        ]

    )
    )
    
    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('delete_schedule', start_deleting_scheduled_update)],

        states={
            CHOOSING: [MessageHandler(Filters.text,
                                      deleting_scheduled_update)]
        },

        fallbacks=[MessageHandler(Filters.regex('^Exit$'), cancel_deleting_scheduler),
        ]

    )
    )

    updater.dispatcher.add_handler(CommandHandler("delete_all", deleting_all_scheduler))
    
    run(updater)


