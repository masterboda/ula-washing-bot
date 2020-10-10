import re
import datetime
import threading

import telegram

from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters
)

from .config import TOKEN
from .commands import (
    start,
    help
)

""" Logging setup
========================================="""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater = Updater(token=TOKEN, use_context=True)

""" Stop the Bot
========================================="""


def shutdown():
    updater.stop()
    updater.is_idle = False


def stop(update: telegram.Update, context: CallbackContext):
    context.bot.send_message(update.effective_chat.id, "Bot is going to stop. Bye!")
    threading.Thread(target=shutdown).start()


def main():
    # Command Handlers
    updater.dispatcher.add_handler(CommandHandler('stop', stop))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    # Message Handlers
    # ...

    updater.start_polling()


if __name__ == '__main__':
    main()
