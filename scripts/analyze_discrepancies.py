import os
import sqlite3
import yaml

def load_config(root_dir):
    """Loads the configuration from config.yaml."""
    config_path = os.path.join(root_dir, "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def analyze_app_db_discrepancies(apps_dir, db_path):
    """
    Analyzes discrepancies between application directories and the database.

    This function checks for application directories in `apps_dir` that do not
    have a corresponding entry in the 'applications' table of the database.

    Args:
        apps_dir (str): The path to the directory containing application directories.
        db_path (str): The path to the SQLite database file.
    """
    if not os.path.isdir(apps_dir):
        print(f"Error: Application directory not found at '{apps_dir}'")
        return

    # 1. Get a list of all directories in the 'apps' directory.
    try:
        app_dirs = [d for d in os.listdir(apps_dir) if os.path.isdir(os.path.join(apps_dir, d))]
    except FileNotFoundError:
        print(f"Error: Could not list directories in '{apps_dir}'")
        return

    # 2. Connect to the database and get registered applications.
    if not os.path.exists(db_path):
        print(f"Error: Database not found at '{db_path}'")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT app_name FROM applications")
    # We use a set for efficient lookup
    registered_apps = {row[0] for row in cursor.fetchall()}
    conn.close()

    # 3. Compare the two lists and report discrepancies.
    discrepancies = []
    for app_name in app_dirs:
        if app_name not in registered_apps:
            discrepancies.append(app_name)

    if discrepancies:
        print("Discrepancy Report: The following applications are not registered in the database:")
        for app_name in discrepancies:
            print(f" - {app_name}")
    else:
        print("No discrepancies found. All application directories are registered in the database.")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_config(project_root)

    paths = config['paths']
    db_config = config['database']

    apps_directory = os.path.join(project_root, paths['applications'])
    metadata_dir = os.path.join(project_root, paths['metadata'])
    database_path = os.path.join(metadata_dir, db_config['filename'])

    analyze_app_db_discrepancies(apps_directory, database_path)
