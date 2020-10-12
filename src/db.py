import sqlite3
import sys
import json
import time


class SQLite:
    def __init__(self):
        self.db_file = '/home/brutia/Code/Work/ula-washing-bot/data.db'

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row

        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


def with_db(func):

    def wrapper(*args, **kwargs):
        with SQLite() as cursor:
            # try:
            return func(cursor, *args, **kwargs)
            # except Exception as e:
            #     print('DATABASE ERROR', e)

    return wrapper


@with_db
def get_data(cursor):
    cursor.execute('SELECT * FROM data LIMIT 1')
    data = cursor.fetchone()
    return data


@with_db
def get_active_queue(cursor):
    queue_id = get_data()['active_queue_id']

    if queue_id:
        cursor.execute('SELECT * FROM queues WHERE id = ?', (queue_id,))
        queue = cursor.fetchone()

        return queue

    return None


@with_db
def set_active_queue(cursor, queue_id):
    print('set ID: ', type(queue_id))
    cursor.execute('UPDATE data SET active_queue_id = ?', (queue_id,))


@with_db
def create_queue(cursor, is_active=False):
    cursor.execute('INSERT INTO queues DEFAULT VALUES')

    if is_active:
        cursor.execute('UPDATE data SET active_queue_id = ?', (cursor.lastrowid,))

    return cursor.lastrowid


@with_db
def add_queue_item(cursor, queue_id, user):
    cursor.execute('SELECT queue FROM queues WHERE id = ?', (queue_id,))
    queue = json.loads(cursor.fetchone()['queue'] or '[]')

    if len([*filter(lambda item: item['user_data']['user_id'] == user.id, queue)]) > 0:
        return

    data = {
        'user_data': {
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        },
        'date': time.time(),
        'is_washing': False,
        'wash_start_time': None,
        'is_finished': False
    }
    queue.append(data)

    cursor.execute('UPDATE queues SET queue = ? WHERE id = ?', (json.dumps(queue), queue_id))


@with_db
def remove_queue_item(cursor, queue_id, user):
    cursor.execute('SELECT queue FROM queues WHERE id = ?', (queue_id,))
    queue = cursor.fetchone()['queue']

    if not queue:
        return

    queue = [*filter(lambda item: item['user_data']['user_id'] != user.id, json.loads(queue))]
    cursor.execute('UPDATE queues SET queue = ? WHERE id = ?', (json.dumps(queue), queue_id))


@with_db
def swap_queue_items(cursor, queue_id, user):
    """ Returns id of user to notify """

    cursor.execute('SELECT queue FROM queues WHERE id = ?', (queue_id,))
    queue = cursor.fetchone()['queue']

    if not queue:
        return

    queue = json.loads(queue)

    position = None
    for i, item in enumerate(queue):
        if item['user_data']['user_id'] == user.id:
            position = i
            break

    if position is None or position == (len(queue) - 1):
        return

    item = queue.pop(position)
    queue.insert(position + 1, item)

    cursor.execute('UPDATE queues SET queue = ? WHERE id = ?', (json.dumps(queue), queue_id))

    return queue[position]['user_data']['user_id']


@with_db
def init_db(cursor, reset=False):

    if reset:
        cursor.execute('DROP TABLE IF EXISTS data')
        cursor.execute('DROP TABLE IF EXISTS queues')
        cursor.execute('DROP TABLE IF EXISTS timetables')

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            active_queue_id INT NULL,
            active_timetable INT NULL
        )
        """
    )
    cursor.execute('INSERT INTO data DEFAULT VALUES ')

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS queues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            queue TEXT,
            queue_length INT DEFAULT 0,
            is_finished BOOL DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS timetables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rows TEXT
        )
        """
    )
