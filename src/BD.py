import sqlite3

db = sqlite3.connect('all_chats.db')
cursor = db.cursor()


def try_create():
    cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                        chat_id TEXT,
                        chat_name TEXT,
                        date TEXT
                        )''')
    db.commit()


try_create()
