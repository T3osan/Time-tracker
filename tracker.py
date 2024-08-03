# tracker.py

import time
import sqlite3

class Tracker:
    def __init__(self, id, title, total_hours, completed_hours=0):
        self.id = id
        self.title = title
        self.total_hours = total_hours
        self.completed_hours = completed_hours
        self.start_time = None

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.completed_hours += elapsed / 3600  # Convert seconds to hours
            self.start_time = None
            self.update_db()

    def save_to_db(self):
        conn = sqlite3.connect('trackers.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trackers (title, total_hours, completed_hours)
            VALUES (?, ?, ?)
        ''', (self.title, self.total_hours, self.completed_hours))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def update_db(self):
        conn = sqlite3.connect('trackers.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE trackers
            SET title = ?, total_hours = ?, completed_hours = ?
            WHERE id = ?
        ''', (self.title, self.total_hours, self.completed_hours, self.id))
        conn.commit()
        conn.close()

    def delete_from_db(self):
        conn = sqlite3.connect('trackers.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM trackers WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_trackers():
        conn = sqlite3.connect('trackers.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, total_hours, completed_hours FROM trackers')
        trackers = cursor.fetchall()
        conn.close()
        return [Tracker(id, title, total_hours, completed_hours) for id, title, total_hours, completed_hours in trackers]

    def formatted_progress(self):
        total_seconds = int(self.completed_hours * 3600)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

def setup_db():
    conn = sqlite3.connect('trackers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trackers (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            total_hours REAL NOT NULL,
            completed_hours REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
