import telegram
import logging
from telegram.ext import Updater
import logging

from getting_compute_data import getting_netdata_data, plotting_cpu_vs_time

import json
import sys


from telegram.ext import CommandHandler



bot = telegram.Bot(token='948997656:AAFIlbVmFVARJdJQ6A531oyI2UDXeV0icEE')

if __name__=='__main__':

    updater = Updater(token='948997656:AAFIlbVmFVARJdJQ6A531oyI2UDXeV0icEE', use_context=True)
    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)


    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
        
    def custom(update, context):
        photo = open(r'C:\Users\abhi\Desktop\Prakhu Astra\astra_website\15250.jpg', 'rb')
        context.bot.send_message(chat_id=update.effective_chat.id, text="Henlo!!!")
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)

    def sending_a_graph(update, context):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=plotting_cpu_vs_time())

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    custom_handler = CommandHandler('custom', custom)
    dispatcher.add_handler(custom_handler)
    
    cpu_stat_handler = CommandHandler('cpu', sending_a_graph)
    dispatcher.add_handler(cpu_stat_handler)

    updater.start_polling()
