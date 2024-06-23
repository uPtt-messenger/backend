import datetime
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Tuple


class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self._create_table()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(os.path.join('data', f'{self.db_name}.db'))
        try:
            yield conn
        finally:
            conn.close()

    def _create_table(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sender TEXT NOT NULL,
                 receiver TEXT NOT NULL,
                 message TEXT NOT NULL,
                 timestamp TIMESTAMP NOT NULL)''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender_receiver ON chat_messages(sender, receiver)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_messages(timestamp)')
            conn.commit()

    def insert_message(self, sender: str, receiver: str, message: str, timestamp: Optional[datetime.datetime] = None):
        if not all([sender, receiver, message]):
            raise ValueError("Sender, receiver, and message must not be empty")

        if timestamp is None:
            timestamp = datetime.datetime.now()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO chat_messages (sender, receiver, message, timestamp)
                 VALUES (?, ?, ?, ?)''', (sender, receiver, message, timestamp))
            conn.commit()

    def get_messages(self, user1: str, user2: str, limit: int = 100) -> List[Tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM chat_messages
                WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
                ORDER BY timestamp DESC LIMIT ?
            ''', (user1, user2, user2, user1, limit))
            return cursor.fetchall()

    def get_messages_by_date_range(self, user1: str, user2: str, start_date: datetime.datetime,
                                   end_date: datetime.datetime) -> List[Tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM chat_messages
                WHERE ((sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?))
                AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (user1, user2, user2, user1, start_date, end_date))
            return cursor.fetchall()

    def clean_old_messages(self, days: int = 30):
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_messages WHERE timestamp < ?', (cutoff_date,))
            conn.commit()


db: Optional[Database] = None
