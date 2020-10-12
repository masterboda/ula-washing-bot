import re
import json

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    Filters
)

from .db import (
    get_active_queue,
    create_queue,
    add_queue_item,
    remove_queue_item,
    swap_queue_items
)

from . import markup
from .markup import initial_markup, in_queue_markup

ADD_TO_QUEUE, IN_QUEUE = range(2)
WASHERS_COUNT = 3
WASHING_TIME = 1 * 60 * 60


def start(update: Update, context: CallbackContext):
    text_lines = [
        'Привіт!',
        'Я допоможу тобі записатися в чергу на прання, а також нагадуватиму коли тобі потрібно його відносити й забирати.',
        'Внизу ти можеш побачити клавіатуру, за допомогою котрої ти можеш обрати дію, яку хочеш виконати'
    ]
    text = '\n\n'.join(text_lines)

    update.message.reply_text(
        text,
        reply_markup=initial_markup
    )
    print(markup.ADD_TO_QUEUE)
    return ADD_TO_QUEUE


def add_to_queue(update: Update, context: CallbackContext):
    queue_id = get_active_queue()['id']
    add_queue_item(queue_id, update.effective_user)

    text = 'Ви в черзі!\nQueue_id: ' + str(queue_id)

    update.message.reply_text(
        text,
        reply_markup=in_queue_markup
    )

    return IN_QUEUE


def skip_queue(update: Update, context: CallbackContext):
    queue_id = get_active_queue()['id']
    next_user_id = swap_queue_items(queue_id, update.effective_user)

    text = 'Ви пропустили чергу!'

    update.message.reply_text(
        text,
        # reply_markup=markup
    )

    context.bot.send_message(
        next_user_id,
        f'@{ update.effective_user.username } помінявся(лась) з вами чергою'
    )
    return IN_QUEUE


def leave_queue(update: Update, context: CallbackContext):
    queue = get_active_queue()
    remove_queue_item(queue['id'], update.effective_user)

    for item in json.loads(queue['queue']):
        if item['user_data']['user_id'] != update.effective_user.id:
            context.bot.send_message(
                item['user_data']['user_id'],
                f'@{ update.effective_user.username } покинув(ла) чергу'
            )

    text = 'Ви покинули чергу!'

    update.message.reply_text(
        text,
        reply_markup=initial_markup
    )
    return ADD_TO_QUEUE


def show_queue(update: Update, context: CallbackContext):
    text = 'Черга:\n\n'
    queue = get_active_queue()
    update.message.reply_text(text + str(queue['queue']))


def other_reply(update: Update, context: CallbackContext):
    text = "Виберіть один із варіантів на клавіатурі"
    update.message.reply_text(text)


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ADD_TO_QUEUE: [
            MessageHandler(Filters.regex(f'^{ markup.ADD_TO_QUEUE }'), add_to_queue)
        ],
        IN_QUEUE: [
            MessageHandler(Filters.regex(f'^{ markup.SKIP_QUEUE }'), skip_queue),
            MessageHandler(Filters.regex(f'^{ markup.LEAVE_QUEUE }'), leave_queue)
        ]
    },
    fallbacks=[
        MessageHandler(Filters.regex(f'^{ markup.WATCH_QUEUE }'), show_queue),
        MessageHandler(Filters.all, other_reply)
    ]
)
