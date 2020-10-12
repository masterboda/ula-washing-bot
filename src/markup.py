from telegram import KeyboardButton, ReplyKeyboardMarkup

ADD_TO_QUEUE, WATCH_QUEUE, SKIP_QUEUE, SET_WASHING, WASHING_FINISHED, LEAVE_QUEUE = (
    'Записатись у чергу',
    'Переглянути чергу',
    'Пропустити чергу',
    'Закласти прання',
    'Прання завершилось',
    'Покинути чергу'
)

initial_markup = ReplyKeyboardMarkup([
    [ADD_TO_QUEUE, WATCH_QUEUE]
])

in_queue_markup = ReplyKeyboardMarkup([
    [WATCH_QUEUE, SKIP_QUEUE, LEAVE_QUEUE]
])

ready_markup = ReplyKeyboardMarkup([
    [SET_WASHING, WATCH_QUEUE, SKIP_QUEUE, LEAVE_QUEUE]
])

in_progress_markup = ReplyKeyboardMarkup([
    [WASHING_FINISHED, WATCH_QUEUE]
])
