import sqlite3

DB_NAME = "books_history.db"

def init_db():
    """Creates the table structure if it doesn't exist yet."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_prompt TEXT,
            book_title TEXT,
            author TEXT,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_log(user_prompt, title, author, reason):
    """Inserts a new AI recommendation record into the DB."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recommendations (user_prompt, book_title, author, reason)
        VALUES (?, ?, ?, ?)
    ''', (user_prompt, title, author, reason))
    conn.commit()
    conn.close()

def fetch_history():
    """Retrieves all historical searches from latest to oldest."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_prompt, book_title, author, reason FROM recommendations ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows