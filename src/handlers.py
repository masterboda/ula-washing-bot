from telegram import Update, KeyboardButton, ReplyKeyboardMarkup

from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    Filters
)

from .db import (
    get_active_queue,
    set_active_queue,
    create_queue,
    update_queue
)

from .markup import main_markup, in_queue_markup

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
        reply_markup=main_markup
    )

    return ADD_TO_QUEUE


def add_to_queue(update: Update, context: CallbackContext):
    queue = get_active_queue()

    if queue:
        pass
    else:
        queue = create_queue()

    text = 'Ви в черзі!'

    update.message.reply_text(
        text,
        reply_markup=in_queue_markup
    )

    return IN_QUEUE


def skip_queue(update: Update, context: CallbackContext):
    text = 'Ви пропустили чергу!'

    update.message.reply_text(
        text,
        # reply_markup=markup
    )
    return IN_QUEUE


def leave_queue(update: Update, context: CallbackContext):
    text = 'Ви покинули чергу!'

    update.message.reply_text(
        text,
        reply_markup=main_markup
    )
    return ADD_TO_QUEUE


def other_reply(update: Update, context: CallbackContext):
    text = "Виберіть один із варіантів на клавіатурі"
    update.message.reply_text(text)


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ADD_TO_QUEUE: [
            MessageHandler(Filters.regex('^Записатись у чергу'), add_to_queue)
        ],
        IN_QUEUE: [
            MessageHandler(Filters.regex('^Пропустити чергу'), skip_queue),
            MessageHandler(Filters.regex('^Покинути чергу'), leave_queue)
        ]
    },
    fallbacks={
        MessageHandler(Filters.all, other_reply)
    }
)
