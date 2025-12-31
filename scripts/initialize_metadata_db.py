import sqlite3
import os
import yaml

def load_config(root_dir):
    """Loads the configuration from config.yaml."""
    config_path = os.path.join(root_dir, "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def initialize_database(db_path):
    """
    Initializes the SQLite database and creates the necessary tables.

    Args:
        db_path (str): The path to the SQLite database file.
    """
    # Ensure the directory for the database exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the 'applications' table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'new',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create a trigger to automatically update the 'updated_at' timestamp
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS update_applications_updated_at
    AFTER UPDATE ON applications
    FOR EACH ROW
    BEGIN
        UPDATE applications SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """)

    conn.commit()
    conn.close()

    print(f"Database initialized successfully at '{db_path}'")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_config(project_root)

    paths = config['paths']
    db_config = config['database']

    metadata_dir = os.path.join(project_root, paths['metadata'])
    database_path = os.path.join(metadata_dir, db_config['filename'])

    initialize_database(database_path)
