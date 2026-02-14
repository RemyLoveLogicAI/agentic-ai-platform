import sqlite3
import os
import yaml

def load_config(root_dir):
    """Loads the configuration from config.yaml."""
    config_path = os.path.join(root_dir, "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def verify_schema(db_path):
    """
    Verifies and prints the schema of the 'applications' table.
    """
    if not os.path.exists(db_path):
        print(f"Database file not found at '{db_path}'")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query the schema from the sqlite_master table
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='applications';")
    result = cursor.fetchone()

    if result:
        print("Schema for 'applications' table:")
        print(result[0])
    else:
        print("Table 'applications' not found.")

    # also check the trigger
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name='update_applications_updated_at';")
    result = cursor.fetchone()
    if result:
        print("\nSchema for 'update_applications_updated_at' trigger:")
        print(result[0])
    else:
        print("\nTrigger 'update_applications_updated_at' not found.")

    conn.close()

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_config(project_root)

    paths = config['paths']
    db_config = config['database']

    metadata_dir = os.path.join(project_root, paths['metadata'])
    database_path = os.path.join(metadata_dir, db_config['filename'])

    verify_schema(database_path)
