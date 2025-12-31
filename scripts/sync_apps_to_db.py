import os
import sqlite3
import yaml

def load_config(root_dir):
    """Loads the configuration from config.yaml."""
    config_path = os.path.join(root_dir, "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def sync_apps_with_db(apps_dir, db_path):
    """
    Synchronizes application directories with the database.

    This function finds application directories in `apps_dir` that are not
    in the database and adds them.

    Args:
        apps_dir (str): Path to the directory containing application directories.
        db_path (str): Path to the SQLite database file.
    """
    if not os.path.isdir(apps_dir):
        print(f"Error: Application directory not found at '{apps_dir}'")
        return

    try:
        app_dirs = [d for d in os.listdir(apps_dir) if os.path.isdir(os.path.join(apps_dir, d))]
    except FileNotFoundError:
        print(f"Error: Could not list directories in '{apps_dir}'")
        return

    if not os.path.exists(db_path):
        print(f"Error: Database not found at '{db_path}'")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT app_name FROM applications")
    registered_apps = {row[0] for row in cursor.fetchall()}

    new_apps_added = []
    for app_name in app_dirs:
        if app_name not in registered_apps:
            try:
                cursor.execute("INSERT INTO applications (app_name) VALUES (?)", (app_name,))
                new_apps_added.append(app_name)
            except sqlite3.IntegrityError:
                # This could happen in a race condition if another process adds the app.
                print(f"Warning: Could not add '{app_name}'. It might already exist.")

    if new_apps_added:
        conn.commit()
        print("Synchronization complete. The following new applications were registered:")
        for app_name in new_apps_added:
            print(f" - {app_name}")
    else:
        print("No new applications found to register. Database is already in sync.")

    conn.close()

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_config(project_root)

    paths = config['paths']
    db_config = config['database']

    apps_directory = os.path.join(project_root, paths['applications'])
    metadata_dir = os.path.join(project_root, paths['metadata'])
    database_path = os.path.join(metadata_dir, db_config['filename'])

    sync_apps_with_db(apps_directory, database_path)
