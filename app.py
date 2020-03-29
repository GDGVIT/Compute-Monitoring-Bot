import logging
import os
import random
import sys

from telegram.ext import Updater, CommandHandler


from getting_compute_data import getting_netdata_data, plotting_cpu_vs_time

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
2) 
"""


def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=intro_text)
        

def cpu_graph(update, context):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=plotting_cpu_vs_time())



if __name__=='__main__':

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("cpu", cpu_graph))

    run(updater)
