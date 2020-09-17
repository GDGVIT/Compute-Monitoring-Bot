import requests
import time
import asyncio
from utils.bot_messages import (
    welcome_message,
    machine_set_up
)

from utils.bot_helper_functions import (
    initialize_variables_for_bot,
    info_for_monitoring,
    metric_to_command,
    image_for_monitoring,
    metric_to_command
)
from utils.bot_helper_functions import (
    CHOOSING,
    TYPING_CHOICE,
    TYPING_REPLY,
    CANCEL,
    DONE,
    default_commands,
    # virtual_memory_plot
)

from utils.bot_helper_functions import (
    CHOOSING_BOT_PARAMS, 
    BOT_REPLY, 
    BOT_ADDITIONAL_OPTIONS, 
    ADD_ONS, 
    CHOOSING_SCHEDULER_PARAMS, 
    TYPING_SCHEDULER_CHOICE, 
    TYPING_SCHEDULER_REPLY
)

from utils.bot_helper_functions import (
    markup_for_ssh_setup,
    image_for_monitoring,
    metric_to_command,
    info_for_monitoring
)

from utils.ssh_via_subprocess import (
    check_valid_ssh_and_netdata,
    getting_info_by_command
)

from utils.bot_helper_functions import (
    monitor_choices,
    monitor_markup,
    monitor_reply_keyboard
)

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
import re


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

## Asking for User Ip Address and Password

def start_ip_convo(update, context):
    """Starting the ip conversation cycle"""
    update.message.reply_text(machine_set_up,reply_markup=markup_for_ssh_setup)
    return CHOOSING


def choice_for_read_or_update_details(update, context):
    """Choice to read or update ip and password"""
    user_data = context.user_data
    text = update.message.text
    context.user_data['choice'] = text
    if text == 'Done':
        if 'choice' in user_data:
            del user_data['choice']
        params = ['Ip Address', 'Username', 'Password']
        for i in params:
            if i not in user_data:  
                update.message.reply_text("You did not set all the params! Set up all the required params!", reply_markup=markup_for_ssh_setup)
                return CHOOSING
        
        update.message.reply_text("""Your Ip Address is currently set as {}\n""".format(user_data['Ip Address']))
        update.message.reply_text("""Your Username is currently set as {}\n""".format(user_data['Username']))
        update.message.reply_text("""Your Password is currently set as {}\n""".format(user_data['Password']))
        update.message.reply_text("""Your Port is currently set as {}\n""".format(user_data['Port']))
        update.message.reply_text("Click on /setup to reset the desired parameters, or /monitor to start monitoring!")
        return ConversationHandler.END
    elif text == 'Cancel':
        if 'choice' in user_data:
            del user_data['choice']
            del user_data
        update.message.reply_text("You chose to cancel! Byeeee")
        
        return ConversationHandler.END
    
    update.message.reply_text(
        'You chose to set {}. Please do the same properly'.format(text))

    return TYPING_REPLY

def sanity_check(string):
    return bool(re.match('^((\d{1,3}\.){3}\d{1,3})|^[0-9a-zA-Z]+[(\.)(0-9a-zA-Z)]+$', string))

def sanity_check_1(string):
    for i in [' ', "'", '"']:
        if i in string:
            return False
    return True

def storing_or_modifying_details(update, context):
    """Function to store the user choice in memory"""

    user_data = context.user_data
    text = (update.message.text).strip(' ')
    category = user_data['choice']
    
    if category == 'Username':
        if not sanity_check_1(text):
            user_data['Username'] = 'something'
            user_data['Port'] = 22
            update.message.reply_text("You set an improper Username. Please change it.", reply_markup=markup_for_ssh_setup)
            del user_data['choice']
            return CHOOSING
        else:
            user_data['Username'] = text
            user_data['Port'] = 22
            update.message.reply_text("You set Username as {}".format(text), reply_markup=markup_for_ssh_setup)
            del user_data['choice']
            return CHOOSING
    elif category == 'Password':
        if not sanity_check_1(text):
            user_data['Password'] = 'something'
            update.message.reply_text("You set an improper Password. Please change it.", reply_markup=markup_for_ssh_setup)
            del user_data['choice']
            return CHOOSING
        else:
            user_data['Password'] = text
            update.message.reply_text("You set Password as {}".format(text), reply_markup=markup_for_ssh_setup)
            del user_data['choice']
            return CHOOSING 
    elif category == 'Ip Address':
        if not sanity_check(text):
                user_data['Ip Address'] = 'something'
                update.message.reply_text("You set a wrong Ip Address as {}. Please change it.", reply_markup=markup_for_ssh_setup)
                del user_data['choice']
                return CHOOSING 
        else:
            user_data['Ip Address'] = text
            update.message.reply_text("You set Ip Address as {}".format(text), reply_markup=markup_for_ssh_setup)
            del user_data['choice']
            return CHOOSING
    elif category == 'Port':
        if text.isnumeric():
            user_data['Port'] = text
            update.message.reply_text("You set Port as {}".format(text), reply_markup=markup_for_ssh_setup)
            del user_data['choice']
            return CHOOSING
        else:
            update.message.reply_text(update.message.reply_text("You set Port which is invalid. Please change it.", reply_markup=markup_for_ssh_setup))
            del user_data['choice']
            return CHOOSING

def cancel_ip_convo(update, context):
    update.message.reply_text("Some unexpected error occured, restart the bot!")
    return ConversationHandler.END

### SSH_INTO_SERVER_AND_GET_INFO

# def sample_check(update, context):
#     picture = virtual_memory_plot()
#     if 'success' in picture:
#         return context.bot.send_photo(chat_id=update.effective_chat.id, photo=picture['success'])
#     else:
#         print(picture['error'])
#         return update.message.reply_text(picture['error'])


## Monitoring Part
def start_bot_for_monitoring(update, context):
    user_data = context.user_data
    # This takes care to check if user ip address is there in memory or not.    
    if 'Ip Address' not in user_data:
        update.message.reply_text("SSH Parameters not set. Please use /setup to set the necessary details of the system to monitor")  
        return ConversationHandler.END  
    else:   
        ip_address = user_data['Ip Address']
        # Checking if Ip address is a valid regex, and setting up initial parameters
        username, password, host, port = user_data['Username'], user_data['Password'], ip_address, user_data['Port']
        update.message.reply_text("Please Wait while we ping your vm and check necessary configuration for {} ..........".format(ip_address))
        k = asyncio.run(check_valid_ssh_and_netdata(username, password, host, port))
        if 'success' in k:
            # Making arrangements to store parameters asked by bot
            initialize_variables_for_bot(update, context)
            # Variables initialized in memory, preparing to send welcome message to user
            update.message.reply_text("No configuration errors for {}, Ready to proceed!".format(ip_address))
            update.message.reply_text("Please enter your choice based on the above instructions", \
                reply_markup = monitor_markup, one_time_keyboard = True)
            return CHOOSING_BOT_PARAMS
        else:
            print(k['error'])
            update.message.reply_text("Some unknown error occured, please check your details as well as if your server is up or not!")
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
                return CHOOSING_BOT_PARAMS
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
            reply_markup = monitor_markup, one_time_keyboard = True)
        return BOT_REPLY



def get_bot_response(update, context):
    user_data = context.user_data
    state = user_data['monitor']['state']
    user_response = update.message.text

    print(8)

    if user_response == 'Yes':
        print(9)
        if state == 'Done':
            print(10)
            if len(set(user_data['monitor']['monitor_variables'])) == 0:
                print(11)
                # Do something  for no params selected
                update.message.reply_text('You did not select anything, so nothing to show')
                update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup,one_time_keyboard=True)
                return CHOOSING_BOT_PARAMS
            else:
                print(12)
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
            print(13)
            update.message.reply_text('You chose to exit, thank you for using our bot. Byeee!!')
            return ConversationHandler.END
        

        elif state == 'non-initial':
            print(14)
            update.message.reply_text('Cool, You chose to add it.')
            update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup, one_time_keyboard=True)
            return CHOOSING_BOT_PARAMS
        
    
    elif user_response == 'No':
        print(15)
        if state == 'Done':
            print(16)
            update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup, one_time_keyboard=True)
            return CHOOSING_BOT_PARAMS
            # return select_bot_parameter
        
        elif state == 'Exit':
            print(17)
            update.message.reply_text('I guess you would like to explore our bot further.')
            update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup, one_time_keyboard=True)

            return CHOOSING_BOT_PARAMS
            # return select_bot_parameter
        
        elif state == 'non-initial':
            print(18)
            user_data['monitor']['monitor_variables'].remove(user_data['monitor']['monitor_variables'][-1])
            update.message.reply_text('Removed item successfully')
            update.message.reply_text('Please select something from the list to monitor or choose exit if you wish to exit',\
                    reply_markup=monitor_markup, one_time_keyboard=True)
            return CHOOSING_BOT_PARAMS
        

            
def select_bot_actions_after_monitoring_params_selection(update, context):
    user_data = context.user_data
    state = user_data['monitor']['state']
    user_response = update.message.text

    print(19)
    if user_response == 'Add ons':
        print(20)
        update.message.reply_text('You selected Add on')
        update.message.reply_text('Please select something to add on',\
                    reply_markup=ReplyKeyboardMarkup([['Add Visual Graphics'],['Schedule Monitoring'],['Exit']], one_time_keyboard=True))
        return ADD_ONS
    elif user_response == 'Begin Monitoring':
        print(21)
        # do monitoring stuff here
        update.message.reply_text('You selected Begin Monitoring')
        ip_address = user_data['Ip Address']
        monitor_choices_to_display = user_data['monitor']['monitor_variables']

        ##### Change this Part here according to the problem
        if 'Visual Graphics' in user_data['monitor']['add_ons']:
            print(22)
            for i in monitor_choices_to_display:
                update.message.reply_text('Please wait while we fetch the statistics from our server for {} with necessary graphics......'.format(i))
                data = asyncio.run(getting_info_by_command(
                    user_data['Username'],
                    user_data['Password'],
                    user_data['Ip Address'],
                    metric_to_command(i, user_data['Password']),
                    user_data['Port']
                ))
                if 'error' in data:
                    update.message.reply_text(data['error'])
                    return ConversationHandler.END
                data = data['success']
                output = info_for_monitoring(i, data)
                for j in output:
                    if not j:
                        pass
                    else:
                        update.message.reply_text(j)
                picture = image_for_monitoring(
                    i,
                    user_data['Username'],
                    user_data['Password'],
                    user_data['Ip Address'],
                    user_data['Port']
                    )
                if 'success' in picture:
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=picture['success'])
                else:
                    print(picture['error'])
                    update.message.reply_text(picture['error'])
        else:
            print(23)
            for i in monitor_choices_to_display:
                update.message.reply_text('Please wait while we fetch the statistics from our server for {}......'.format(i))
                data = asyncio.run(getting_info_by_command(
                    user_data['Username'],
                    user_data['Password'],
                    user_data['Ip Address'],
                    metric_to_command(i, user_data['Password']),
                    user_data['Port']
                ))
                if 'error' in data:
                    update.message.reply_text(data['error'])
                    return ConversationHandler.END
                data = data['success']
                output = info_for_monitoring(i, data)
                for j in output:
                    if not j:
                        pass
                    else:
                        update.message.reply_text(j)
        return ConversationHandler.END
    elif user_response == 'Exit':
        print(24)
        update.message.reply_text('You chose to exit, thank you for using our bot. Byeee!!')
        return ConversationHandler.END
    else:
        print(25)
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
    
    # Change this part for schedule monitoring
    if user_response == 'Schedule Monitoring':
        return update.message.reply_text("Coming Soon!! Make a PR if you have an idea at this!! ")
        # schedule_monitoring = {}
        # user_data['monitor']['schedule_monitoring'] = True
        # ip_address = user_data['Ip Address']
        # update.message.reply_text("You chose to create a new scheduler for the system {}".format(ip_address),\
        #     reply_markup=scheduler_markup)
        # update.message.reply_text('Please select a unique name for your scheduler. Click on the name button to set a new name, or you can still go back',\
        #             reply_markup=ReplyKeyboardMarkup([['Name of the Event'],['Go Back']]),\
        #                 one_time_keyboard=True)
        # return CHOOSING_SCHEDULER_PARAMS
        
    elif user_response == 'Exit':
        update.message.reply_text('You chose to exit add ons')
        reply_markup=ReplyKeyboardMarkup([['Add ons'],['Begin Monitoring'],['Exit']],\
            one_time_keyboard=True)
        return BOT_ADDITIONAL_OPTIONS

def cancel(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    
    if 'Ip Address' in user_data:
        update.message.reply_text("""You Ip Address is currently set as {}\n.User /monitor to start monitoring values""".format(user_data['Ip Address']))
    else:
        update.message.reply_text("You chose to cancel.")
    return ConversationHandler.END


# Creating a Scheduler
# scheduler_reply_keyboard = [['Minute', 'Hour'], ['Day of Month'], ['Select A Month','Mode'], ['Confirm','Exit']]
# scheduler_markup = ReplyKeyboardMarkup(scheduler_reply_keyboard, one_time_keyboard=True)

# def choosing_schedule_parameters(update, context):
#     text = update.message.text
#     if text == 'Go Back':
#         update.message.reply_text('Please select something an add on',\
#                     reply_markup=ReplyKeyboardMarkup([['Add Visual Graphics'],\
#                         ['Schedule Monitoring'],\
#                             ['Exit']]),one_time_keyboard=True)
#         return ADD_ONS
#     else:
#         context.user_data['choice'] = text
#         update.message.reply_text('Please enter {}'.format(text))

#         return TYPING_SCHEDULER_REPLY


# def setting_up_scheduler_parameter_value(update, context):
#     text = update.message.text
#     user_data = context.user_data
#     user_data[user_data['choice']] = text

#     # Put checks for the values of params
#     update.message.reply_text("You set {} as {}".format(
#         user_data['choice'], user_data[user_data['choice']]),reply_markup=scheduler_markup)
#     del user_data['choice']

#     return CHOOSING_SCHEDULER_PARAMS


# def checking_if_all_scheduler_options_present(context):
#     user_data = context.user_data
#     print(user_data)
#     params = ['Name of the Event', 'Mode']
#     for i in params:
#         if i not in user_data:
#             return False
#     return True

# def cancel_setting_scheduler(update, context):
#     user_data = context.user_data
#     if 'choice' in user_data:
#         del user_data['choice']
    
#     update.message.reply_text("You chose to cancel")
#     return ConversationHandler.END

# def confirm_setting_scheduler(update, context):
#     user = update.message.from_user
#     user_id = user['id']
#     user_data = context.user_data
#     ip_address = user_data['Ip Address']

#     # Put checks for the values of params
#     if 'Minute' not in user_data:
#         minute = '*'
#     else:
#         minute = user_data['Minute']
    
#     if 'Hour' not in user_data:
#         hour = '*'
#     else:
#         hour = user_data['Hour']
    
#     if 'Day of Month' not in user_data:
#         day_of_month = '*'
#     else:
#         day_of_month = user_data['Day of Month']

#     if 'Select A Month' not in user_data:
#         select_a_month = '*'
#     else:
#         select_a_month = user_data['Select A Month']
    
#     if 'Mode' not in user_data:
#         mode = '1'
#     else:
#         mode = user_data['Mode']
    
#     params = {
#         'Minute': minute,
#         'Hour': hour,
#         'Day of Month': day_of_month,
#         'Select A Month': select_a_month,
#         'Mode': mode
#     }
#     print("Scheduler confirm 1")
#     if len(set(params.values())) == 1:
#         if '0' not in params.values():
#             pass
#         else:
#             print("Scheduler confirm 2")
#             update.message.reply_text("Cannot confirm with all settings as 0", reply_markup=scheduler_markup)
#             return CHOOSING_SCHEDULER_PARAMS
#     else:
#         for i in params:
#             if params[i] == '0':
#                 user_data[i] = '*'
#         print("Scheduler confirm 3")
    
#     if checking_if_all_scheduler_options_present(context):
#         params = {
#             'user_id': user_id,
#             'file_name': 'cron_jobs.py',
#             'name_of_job': user_data['Name of the Event'],
#             'minute': minute,
#             'hour': hour,
#             'day_of_month': day_of_month,
#             'month': select_a_month,
#             'mode': mode
#         }
#         print(params)
#         output = making_a_cron_job(ip_address,params)
#         update.message.reply_text(output[1])
#         return ConversationHandler.END
#     else:
#         update.message.reply_text("All Required Parameters not set, Name and Mode Required!", reply_markup=scheduler_markup, one_time_keyboard=True)
#         return CHOOSING_SCHEDULER_PARAMS


# def start_deleting_scheduled_update(update, context):
#     user_data = context.user_data
#     if 'Ip Address' not in user_data:
#         update.message.reply_text("Ip not set. Please user /setIp to set the Ip of the system to delete scheduled monitoring")    
#     else:
#         ip_address = user_data['Ip Address']
#         if check_ip(ip_address):
#             update.message.reply_text("You chose to delete a scheduler for the system {}. Please enter the name of the scheduler".format(ip_address))
#             return CHOOSING
#         else:
#             update.message.reply_text("You set up an improper Ip, please setup a proper one at /setIp")


# def deleting_scheduled_update(update, context):
#     name = update.message.text+' #set by Bot'
#     user_data = context.user_data
#     ip_address = user_data['Ip Address']
#     output = deleting_a_cron_job(ip_address, name)
#     update.message.reply_text(output[1])
#     return ConversationHandler.END

# def cancel_deleting_scheduler(update, context):
#     user_data = context.user_data
#     if 'choice' in user_data:
#         del user_data['choice']
    
#     update.message.reply_text("You chose to cancel")
#     return ConversationHandler.END


# Deleting all scheduler
# def deleting_all_scheduler(update, context):
#     user_data = context.user_data
#     if 'Ip Address' not in user_data:
#         update.message.reply_text("Ip not set. Please user /setIp to set the Ip of the system to delete all scheduled monitoring")    
#     else:
#         ip_address = user_data['Ip Address']
#         output = deleting_all_cron_jobs(ip_address)
#         if output:
#             update.message.reply_text("Successfully Deleted all Scheduled Monitors")
#         else:
#             update.message.reply_text("Error in  deleting all Scheduled Monitors")
