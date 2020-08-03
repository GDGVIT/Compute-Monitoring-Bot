import requests
from utils.bot_messages import (
    welcome_message,
    machine_set_up
)
from utils.bot_helper_functions import (
    CHOOSING,
    TYPING_CHOICE,
    TYPING_REPLY,
    CANCEL,
    DONE,
    default_commands
)

from utils.bot_helper_functions import (
    markup_for_ssh_setup
)

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler


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
        update.message.reply_text("Click on /setup to reset the desired parameters, or /monitor to start monitoring!")
        return ConversationHandler.END
    elif text == 'Cancel':
        if 'choice' in user_data:
            del user_data['choice']
        update.message.reply_text("You chose to cancel! Byeeee")
        
        return ConversationHandler.END
    
    update.message.reply_text(
        'You chose to {}. Please do the same properly'.format(text))

    return TYPING_REPLY


def storing_or_modifying_details(update, context):
    """Function to store the user choice in memory"""

    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    
    if category == 'Username':
        user_data['Username'] = text
        update.message.reply_text("You set Username as {}".format(text), reply_markup=markup_for_ssh_setup)
    elif category == 'Password':
        user_data['Password'] = text
        update.message.reply_text("You set Password as {}".format(text), reply_markup=markup_for_ssh_setup)
    elif category == 'Ip Address':
        user_data['Ip Address'] = text
        update.message.reply_text("You set Ip Address as {}".format(text), reply_markup=markup_for_ssh_setup)
    del user_data['choice']
    return CHOOSING

def cancel_ip_convo(update, context):
    update.message.reply_text("Some unexpected error occured, restart the bot!")
    return ConversationHandler.END

### SSH_INTO_SERVER_AND_GET_INFO

def get_info_from_ssh_server(username, hostname, password, commands=default_commands):
    params = {
        "username": username,
        "hostname": hostname,
        "password": password,
        "commands": commands
    }
    url = 'http://127.0.0.1:5000/exec'
    response = requests.post(url, data=params)
    print(response.text)
    return response

### Returning Info Back

def running_remote_commands(update, context):
    """Function to return the user choice in memory"""
    user_data = context.user_data
    update.message.reply_text('Wait while we get info from the server!')
    update.message.reply_text(get_info_from_ssh_server(
        user_data['Username'],
        user_data['Password'],
        user_data['Ip Address'],
        ['uname'] 
        ).text)
    