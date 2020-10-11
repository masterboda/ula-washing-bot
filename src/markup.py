from telegram import KeyboardButton, ReplyKeyboardMarkup

ADD_TO_QUEUE, WATCH_QUEUE, SKIP_QUEUE, LEAVE_QUEUE = (
    'Записатись у чергу',
    'Переглянути чергу',
    'Пропустити чергу',
    'Покинути чергу'
)

main_markup = ReplyKeyboardMarkup([
    [ADD_TO_QUEUE]
])

in_queue_markup = ReplyKeyboardMarkup([
    [WATCH_QUEUE, SKIP_QUEUE, LEAVE_QUEUE]
])
