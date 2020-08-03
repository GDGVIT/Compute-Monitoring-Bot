CHOOSING, TYPING_REPLY, TYPING_CHOICE, DONE, CANCEL = range(5)

from telegram import ReplyKeyboardMarkup
reply_keyboard_for_ssh_setup = [['Username', 'Password', 'Ip Address'],
                  ['Cancel', 'Done']]
markup_for_ssh_setup = ReplyKeyboardMarkup(reply_keyboard_for_ssh_setup, one_time_keyboard=True)


default_commands = [
    "curl http://localhost:19999/api/v1/data?chart=system.cpu",
    "curl http://localhost:19999/api/v1/data?chart=system.ram"
    ]