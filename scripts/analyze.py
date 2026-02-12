import sqlite3
import os
import sys
import configparser
import datetime

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

def get_app_id(conn, app_name):
    """Gets the application ID from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM applications WHERE name = ?", (app_name,))
    result = cursor.fetchone()
    if result:
        return result['id']
    return None

def add_discrepancy(conn, app_id, description):
    """Adds a discrepancy to the database."""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO discrepancies (app_id, description) VALUES (?, ?)", (app_id, description))
    print(f"Discrepancy added: {description}")

def update_app_status(conn, app_id, status):
    """Updates the application status in the database."""
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
    print(f"Application status updated to '{status}'")

def analyze_readme(conn, app_id, app_path):
    """Checks for the presence of a README.md file."""
    readme_path = os.path.join(app_path, 'README.md')
    if not os.path.exists(readme_path):
        add_discrepancy(conn, app_id, "Missing README.md file.")

def analyze_todos(conn, app_id, app_path):
    """Scans for 'TODO' comments in source files."""
    for root, _, files in os.walk(app_path):
        for file in files:
            # Simple check for text files, can be improved
            if file.endswith(('.py', '.js', '.txt', '.md')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f):
                            if 'TODO' in line:
                                add_discrepancy(conn, app_id, f"Found 'TODO' in {file} on line {i+1}: {line.strip()}")
                except Exception as e:
                    print(f"Could not read file {filepath}: {e}")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <application_name>")
        sys.exit(1)

    app_name = sys.argv[1]
    app_path = os.path.join(APPS_DIR, app_name)

    if not os.path.isdir(app_path):
        print(f"Error: Application '{app_name}' not found in '{APPS_DIR}'.")
        sys.exit(1)

    conn = get_db_connection()
    app_id = get_app_id(conn, app_name)

    if not app_id:
        print(f"Error: Application '{app_name}' not registered in the database.")
        conn.close()
        sys.exit(1)

    print(f"Analyzing application: {app_name}")

    # Run analyses
    analyze_readme(conn, app_id, app_path)
    analyze_todos(conn, app_id, app_path)

    # Update status
    update_app_status(conn, app_id, 'analyzed')

    conn.commit()
    conn.close()
    print("Analysis complete.")

if __name__ == "__main__":
    main()
