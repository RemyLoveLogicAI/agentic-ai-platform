import sqlite3
import os
import datetime
import configparser

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

DB_PATH = config['Paths']['database']
APPS_DIR = config['Paths']['applications_dir']

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the necessary tables in the database if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        path TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'new'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        note TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (app_id) REFERENCES applications (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discrepancies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        description TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (app_id) REFERENCES applications (id)
    );
    """)

    conn.commit()
    conn.close()
    print("Tables created successfully.")

def sync_applications():
    """Syncs the applications from the filesystem to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    app_dirs = [d for d in os.listdir(APPS_DIR) if os.path.isdir(os.path.join(APPS_DIR, d))]

    for app_name in app_dirs:
        app_path = os.path.join(APPS_DIR, app_name)
        cursor.execute("SELECT id FROM applications WHERE name = ?", (app_name,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO applications (name, path) VALUES (?, ?)", (app_name, app_path))
            print(f"Registered new application: {app_name}")

    conn.commit()
    conn.close()
    print("Application sync complete.")

if __name__ == "__main__":
    create_tables()
    sync_applications()
