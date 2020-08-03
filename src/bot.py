import logging
import time

import os

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
#from telegram.ext.dispatcher import run_async

from dotenv import load_dotenv
from pathlib import Path
import sys

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from utils.getting_images_for_compute_data import (
    image_for_various_parameters
)


from utils.helper_functions import (
    check_ip,
    probe_server,
    making_a_cron_job,
    deleting_a_cron_job,
    deleting_all_cron_jobs,
    getting_current_data_from_server,
    user_choice_for_monitoring_regex_check,
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


from utils.getting_data_from_client import (
    get_available_choices_to_monitor_list,
    get_available_choices_to_monitor,
    respond_to_server_request
)

from utils.getting_compute_data import (
    plotting_cpu_vs_time_without_ssh
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


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message_extension)
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message_second_extension)

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message_extension)
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_start_message_second_extension)


CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

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
        if ':' in text:
            text = '['+text+']'
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
        update.message.reply_text("""You Ip Address is currently set as {}\n.User /start_monitoring to start monitoring values""".format(user_data['ip_address']))
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


def initialize_variables_for_bot(update, context):
    user_data = context.user_data
    user_data['monitor'] = {}
    user_data['monitor']['state'] = 'initial'
    user_data['monitor']['user_response'] = ''
    user_data['monitor']['monitor_variables'] = []
    user_data['monitor']['add_ons'] = []
    user_data['monitor']['notifications_set'] = {}
    user_data['monitor']['schedule_monitoring'] = False

monitor_reply_keyboard = [['System Information','Virtual Memory Info'],['Boot Time','Cpu Info','Swap Memory'],
['Disk Info','Network Info'], ['Exit', 'Done']]

monitor_choices = ['System Information','Virtual Memory Info','Boot Time','Cpu Info','Swap Memory','Disk Info','Network Info']
monitor_markup = ReplyKeyboardMarkup(monitor_reply_keyboard, one_time_keyboard=True)

CHOOSING_BOT_PARAMS, BOT_REPLY, BOT_ADDITIONAL_OPTIONS, ADD_ONS, CHOOSING_SCHEDULER_PARAMS, TYPING_SCHEDULER_CHOICE, TYPING_SCHEDULER_REPLY  = range(7)

def start_bot_for_monitoring(update, context):
    user_data = context.user_data
    # This takes care to check if user ip address is there in memory or not.    
    if 'ip_address' not in user_data:
        update.message.reply_text("Ip not set. Please user /setIp to set the Ip of the system to monitor")  
        return ConversationHandler.END  
    else:   
        ip_address = user_data['ip_address']
        # Checking if Ip address is a valid regex, and setting up initial parameters
        if check_ip(ip_address):
            # Making arrangements to store parameters asked by bot
            initialize_variables_for_bot(update, context)
            # Variables initialized in memory, preparing to send welcome message to user
            update.message.reply_text("Cool, You chose to start monitoring system {}".format(ip_address))
            update.message.reply_text("Please enter your choice based on the above instructions", \
                reply_markup = monitor_markup)
            return CHOOSING_BOT_PARAMS
        else:
            update.message.reply_text("You set up an improper Ip, please setup a proper one at /setIp")
            return ConversationHandler.END


def select_bot_parameter(update, context):
    user_data = context.user_data
    state = user_data['monitor']['state']
    user_response = update.message.text

    if user_response in monitor_choices:
        print(1)
        if user_response not in user_data['monitor']['monitor_variables']:
            user_data['monitor']['user_response'] = user_response
            user_data['monitor']['monitor_variables'].append(user_response)
            user_data['monitor']['state'] = 'non-initial'
            update.message.reply_text("You have selected " + \
                user_data['monitor']['user_response'])
            print("Changed")
            update.message.reply_text("Are you sure to add "+user_data['monitor']['user_response']+" to the current monitoring list ?",\
                reply_markup=ReplyKeyboardMarkup([['Yes'], ['No']], one_time_keyboard = True))
            return BOT_REPLY
            # choose_options_for_monitoring(update,context)
        else:
            print(2)
            if len(set(user_data['monitor']['monitor_variables'])) == 7:
                print(3)
                user_data['monitor']['state'] = 'Exit'
                update.message.reply_text("Done Selecting monitoring values, looks like you added all params already!")
                user_data['monitor']['state'] = 'Done'
                return BOT_REPLY
                
            else:
                print(4)
                update.message.reply_text('Already Selected! Choose another value.', reply_markup=monitor_markup, one_time_keyboard=True)
                return BOT_REPLY
                #choose_options_for_monitoring(update,context)
                # return bot_response_state
    
    elif user_response == 'Done':
        print(5)
        user_data['monitor']['state'] = 'Done'
        update.message.reply_text('Are you sure you are done selecting items?', \
                reply_markup = ReplyKeyboardMarkup([['Yes'], ['No']], one_time_keyboard = True))
        return BOT_REPLY
        # Do done part here
    elif user_response == 'Exit':
        print(6)
        user_data['monitor']['state'] = 'Exit'
        update.message.reply_text('Are you sure you want to exit?', \
                reply_markup = ReplyKeyboardMarkup([['Yes'], ['No']], one_time_keyboard = True))
        return BOT_REPLY
        # Do exit part here
    else:
        print(7)
        update.message.reply_text('Invalid parameter entered, Please enter only specific parameters provided',\
            reply_markup = monitor_markup)
        return BOT_REPLY



def get_bot_response(update, context):
    user_data = context.user_data
    state = user_data['monitor']['state']
    user_response = update.message.text

    print("Something")

    if user_response == 'Yes':
        if state == 'Done':
            if len(set(user_data['monitor']['monitor_variables'])) == 0:
                # Do something  for no params selected
                update.message.reply_text('You did not select anything, so nothing to show')
                update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup,one_time_keyboard=True)
                return CHOOSING_BOT_PARAMS
            else:
                # Ask for additional params
                bot_response_at_end_of_monitoring = """You have selected these options for monitoring:\n"""
                for i in range(len(set(user_data['monitor']['monitor_variables']))):
                    response_str = str(i+1) + ". " + user_data['monitor']['monitor_variables'][i] + '\n'
                    bot_response_at_end_of_monitoring+=response_str
                update.message.reply_text(bot_response_at_end_of_monitoring)
                # Move to additional params if possible

                update.message.reply_text('Choose your next action' , \
        reply_markup=ReplyKeyboardMarkup([['Add ons'],['Begin Monitoring'],['Exit']]),\
            one_time_keyboard=True)

                return BOT_ADDITIONAL_OPTIONS
        elif state == 'Exit':
            update.message.reply_text('You chose to exit, thank you for using our bot. Byeee!!')
            return ConversationHandler.END
        

        elif state == 'non-initial':
            update.message.reply_text('Cool, You chose to add it.')
            update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup, one_time_keyboard=True)
            return CHOOSING_BOT_PARAMS
        
    
    elif user_response == 'No':
        if state == 'Done':
            update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup, one_time_keyboard=True)
            return CHOOSING_BOT_PARAMS
            # return select_bot_parameter
        
        elif state == 'Exit':
            update.message.reply_text('I guess you would like to explore our bot further.')
            update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup, one_time_keyboard=True)

            return CHOOSING_BOT_PARAMS
            # return select_bot_parameter
        
        elif state == 'non-initial':
            user_data['monitor']['monitor_variables'].remove(user_data['monitor']['monitor_variables'][-1])
            update.message.reply_text('Removed item successfully')
            update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup, one_time_keyboard=True)
            return CHOOSING_BOT_PARAMS
        

            
def select_bot_actions_after_monitoring_params_selection(update, context):
    user_data = context.user_data
    state = user_data['monitor']['state']
    user_response = update.message.text

    if user_response == 'Add ons':
        update.message.reply_text('You selected Add on')
        update.message.reply_text('Please select something an add on',\
                    reply_markup=ReplyKeyboardMarkup([['Add Visual Graphics'],['Schedule Monitoring'],['Exit']]), one_time_keyboard=True)
        return ADD_ONS
    elif user_response == 'Begin Monitoring':
        # do monitoring stuff here
        update.message.reply_text('You selected Begin Monitoring')
        ip_address = user_data['ip_address']
        monitor_choices_to_display = user_data['monitor']['monitor_variables']
        if 'Visual Graphics' in user_data['monitor']['add_ons']:
            for i in monitor_choices_to_display:
                output = getting_current_data_from_server(ip_address, i)
                update.message.reply_text(output)
                image = image_for_various_parameters(i, ip_address)
                if image:
                    update.message.reply_photo(photo=image)
                else:
                    update.message.reply_text("No photo for this parameter")
        else:
            for i in monitor_choices_to_display:
                output = getting_current_data_from_server(ip_address, i)
                update.message.reply_text(output)
        return ConversationHandler.END
    elif user_response == 'Exit':
        update.message.reply_text('You chose to exit, thank you for using our bot. Byeee!!')
        return ConversationHandler.END
    else:
        update.message.reply_text('Invalid Input, Quitting, Byeeee')
        return ConversationHandler.END



def select_bot_response_to_add_ons(update, context):
    user_data = context.user_data
    state = user_data['monitor']['state']
    user_response = update.message.text

    if user_response == 'Add Visual Graphics':
        user_data['monitor']['add_ons'].append('Visual Graphics')
        update.message.reply_text('Visual Graphics Will Now be shown for Monitoring Data !')
        update.message.reply_text('Choose your next action' , \
        reply_markup=ReplyKeyboardMarkup([['Add ons'],['Begin Monitoring'],['Exit']]),\
            one_time_keyboard=True)
        return BOT_ADDITIONAL_OPTIONS
    
    if user_response == 'Schedule Monitoring':
        schedule_monitoring = {}
        user_data['monitor']['schedule_monitoring'] = True
        ip_address = user_data['ip_address']
        update.message.reply_text("You chose to create a new scheduler for the system {}".format(ip_address),\
            reply_markup=scheduler_markup)
        update.message.reply_text('Please select a unique name for your scheduler. Click on the name button to set a new name, or you can still go back',\
                    reply_markup=ReplyKeyboardMarkup([['Name of the Event'],['Go Back']]),\
                        one_time_keyboard=True)
        return CHOOSING_SCHEDULER_PARAMS
        
    elif user_response == 'Exit':
        update.message.reply_text('You chose to exit add ons')
        reply_markup=ReplyKeyboardMarkup([['Add ons'],['Begin Monitoring'],['Exit']],\
            one_time_keyboard=True)
        return BOT_ADDITIONAL_OPTIONS



# Creating a Scheduler
scheduler_reply_keyboard = [['Minute', 'Hour'], ['Day of Month'], ['Select A Month','Mode'], ['Confirm','Exit']]
scheduler_markup = ReplyKeyboardMarkup(scheduler_reply_keyboard, one_time_keyboard=True)

def choosing_schedule_parameters(update, context):
    text = update.message.text
    if text == 'Go Back':
        update.message.reply_text('Please select something an add on',\
                    reply_markup=ReplyKeyboardMarkup([['Add Visual Graphics'],\
                        ['Schedule Monitoring'],\
                            ['Exit']]),one_time_keyboard=True)
        return ADD_ONS
    else:
        context.user_data['choice'] = text
        update.message.reply_text('Please enter {}'.format(text))

        return TYPING_SCHEDULER_REPLY


def setting_up_scheduler_parameter_value(update, context):
    text = update.message.text
    user_data = context.user_data
    user_data[user_data['choice']] = text

    # Put checks for the values of params
    update.message.reply_text("You set {} as {}".format(
        user_data['choice'], user_data[user_data['choice']]),reply_markup=scheduler_markup)
    del user_data['choice']

    return CHOOSING_SCHEDULER_PARAMS


def checking_if_all_scheduler_options_present(context):
    user_data = context.user_data
    print(user_data)
    params = ['Name of the Event', 'Mode']
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
    if 'Minute' not in user_data:
        minute = '*'
    else:
        minute = user_data['Minute']
    
    if 'Hour' not in user_data:
        hour = '*'
    else:
        hour = user_data['Hour']
    
    if 'Day of Month' not in user_data:
        day_of_month = '*'
    else:
        day_of_month = user_data['Day of Month']

    if 'Select A Month' not in user_data:
        select_a_month = '*'
    else:
        select_a_month = user_data['Select A Month']
    
    if 'Mode' not in user_data:
        mode = '1'
    else:
        mode = user_data['Mode']
    
    params = {
        'Minute': minute,
        'Hour': hour,
        'Day of Month': day_of_month,
        'Select A Month': select_a_month,
        'Mode': mode
    }
    print("Scheduler confirm 1")
    if len(set(params.values())) == 1:
        if '0' not in params.values():
            pass
        else:
            print("Scheduler confirm 2")
            update.message.reply_text("Cannot confirm with all settings as 0", reply_markup=scheduler_markup)
            return CHOOSING_SCHEDULER_PARAMS
    else:
        for i in params:
            if params[i] == '0':
                user_data[i] = '*'
        print("Scheduler confirm 3")
    
    if checking_if_all_scheduler_options_present(context):
        params = {
            'user_id': user_id,
            'file_name': 'cron_jobs.py',
            'name_of_job': user_data['Name of the Event'],
            'minute': minute,
            'hour': hour,
            'day_of_month': day_of_month,
            'month': select_a_month,
            'mode': mode
        }
        print(params)
        output = making_a_cron_job(ip_address,params)
        update.message.reply_text(output[1])
        return ConversationHandler.END
    else:
        update.message.reply_text("All Required Parameters not set, Name and Mode Required!", reply_markup=scheduler_markup, one_time_keyboard=True)
        return CHOOSING_SCHEDULER_PARAMS


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


    CHOOSING_BOT_PARAMS, BOT_REPLY, BOT_ADDITIONAL_OPTIONS = range(3)
    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('start_monitoring', start_bot_for_monitoring)],

        states={
           
            CHOOSING_BOT_PARAMS: [MessageHandler(Filters.text,
                                           select_bot_parameter),
                            ],
            BOT_REPLY : [MessageHandler(Filters.text,
                                           get_bot_response),
                            ],
            BOT_ADDITIONAL_OPTIONS : [MessageHandler(Filters.text,
                                           select_bot_actions_after_monitoring_params_selection),
                            ],
            ADD_ONS: [
                MessageHandler(Filters.text,
                    select_bot_response_to_add_ons),
            ],

            CHOOSING_SCHEDULER_PARAMS: [MessageHandler(Filters.regex('^(Name of the Event|Minute|Hour|Day of Month|Select A Month|Mode)$'),
                                      choosing_schedule_parameters),
                                      MessageHandler(Filters.regex('^Confirm$'), confirm_setting_scheduler),
                       ],

            TYPING_SCHEDULER_CHOICE: [MessageHandler(Filters.text,
                                           choosing_schedule_parameters)
                            ],

            TYPING_SCHEDULER_REPLY: [MessageHandler(Filters.text,
                                          setting_up_scheduler_parameter_value),
                           ],


        },

        fallbacks=[MessageHandler(Filters.regex('^Exit$'), cancel)]
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