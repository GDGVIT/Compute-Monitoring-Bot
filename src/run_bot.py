import logging
import time
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv
from pathlib import Path
import sys

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


from utils.bot_helper_functions import (
    CHOOSING,
    TYPING_CHOICE,
    TYPING_REPLY,
    CANCEL,
    DONE
)


from ssh_bot import (
    start,
    running_remote_commands
)

from ssh_bot import (
    start_ip_convo,
    choice_for_read_or_update_details,
    storing_or_modifying_details,
    cancel_ip_convo
)


if __name__=='__main__':

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    # Handler for starting the bot
    updater.dispatcher.add_handler(CommandHandler("start", start))

    # Handler for Credentials setup
    updater.dispatcher.add_handler(
        ConversationHandler(
        entry_points=[CommandHandler('setup', start_ip_convo)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Username|Password|Ip Address|Cancel|Done)$'),
                                      choice_for_read_or_update_details),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           choice_for_read_or_update_details)
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          storing_or_modifying_details),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Exit$'), cancel_ip_convo)]
    )
    )

    # Handler for running remote commands
    updater.dispatcher.add_handler(CommandHandler("run", running_remote_commands))

    run(updater)