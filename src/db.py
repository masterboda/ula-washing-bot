import sqlite3
import json


class SQLite:
    def __init__(self):
        self.db_file = 'data.db'

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


def with_db(func):

    def wrapper(*args, **kwargs):
        with SQLite() as cursor:
            return func(cursor, *args, **kwargs)

    return wrapper


@with_db
def get_active_queue(cursor):
    cursor.execute('SELECT id FROM queues WHERE id = (SELECT active_queue FROM data LIMIT 1)')
    queue_id = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM queue_item WHERE queue_id = ?', queue_id)
    queue_items = cursor.fetchone()

    return queue_id, queue_items


@with_db
def set_active_queue(cursor, queue_id):
    cursor.execute('UPDATE data SET active_queue = ?', queue_id)


@with_db
def create_queue(cursor, data, is_active=False):
    cursor.execute('INSERT INTO queues (data) VALUES (?)', json.dumps(data))

    if is_active:
        set_active_queue(cursor.lastrowid)

    return cursor.lastrowid


@with_db
def update_queue(cursor, new_data, queue_id):
    cursor.execute('UPDATE queues SET data = ? WHERE id = ?', new_data, queue_id)


@with_db
def init_db(cursor, reset=False):

    if reset:
        cursor.execute('DROP TABLE IF EXISTS data')
        cursor.execute('DROP TABLE IF EXISTS queues')
        cursor.execute('DROP TABLE IF EXISTS queue_item')
        cursor.execute('DROP TABLE IF EXISTS timetables')

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            active_queue INT NULL,
            active_timetable INT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS queues (
            id INT AUTO_INCREMENT PRIMARY KEY,
            is_finished BOOl 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS queue_item (
            id INT AUTO_INCREMENT PRIMARY KEY,
            queue_id INT NOT NULL,
            user TEXT NOT NULL,
            date datetime NOT NULL,
            order INT NOT NULL,
            is_washing BOOL 0,
            is_finished BOOL 0,
            wash_start_time datetime
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS timetables (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name TEXT NOT NULL,
            rows TEXT
        )
        """
    )

