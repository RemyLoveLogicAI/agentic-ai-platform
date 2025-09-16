import sqlite3
import yaml
from pathlib import Path
import logging
import tarfile
import shutil
import tempfile
import os
import hashlib

def load_config(config_path='config.yaml'):
    """Loads the configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def init_db(db_path):
    """Initializes the database and creates tables if they don't exist."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT NOT NULL UNIQUE,
        version INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'new',
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        package_path TEXT,
        context_notes TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS file_hashes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_hash TEXT NOT NULL,
        FOREIGN KEY (app_id) REFERENCES applications (id)
    )
    """)
    conn.commit()
    conn.close()
    logging.info(f"Database initialized at {db_path}")

def get_or_create_app(app_name, db_path):
    """Gets an application from the database, or creates a new one."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, version, status FROM applications WHERE app_name = ?", (app_name,))
    result = cursor.fetchone()
    if result:
        app_id, version, status = result
    else:
        cursor.execute("INSERT INTO applications (app_name) VALUES (?)", (app_name,))
        conn.commit()
        app_id = cursor.lastrowid
        version = 1
        status = 'new'
        logging.info(f"Created new application record for {app_name}")
    conn.close()
    return app_id, version, status

def update_app_status(app_id, status, db_path, version=None):
    """Updates the status and optionally the version of an application."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if version:
        cursor.execute("UPDATE applications SET status = ?, version = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?", (status, version, app_id))
    else:
        cursor.execute("UPDATE applications SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?", (status, app_id))
    conn.commit()
    conn.close()

def get_file_hashes(app_id, db_path):
    """Retrieves the file hashes for a given application."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path, file_hash FROM file_hashes WHERE app_id = ?", (app_id,))
    hashes = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return hashes

def update_file_hashes(app_id, hashes, db_path):
    """Updates the file hashes for an application."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM file_hashes WHERE app_id = ?", (app_id,))
    for file_path, file_hash in hashes.items():
        cursor.execute("INSERT INTO file_hashes (app_id, file_path, file_hash) VALUES (?, ?, ?)", (app_id, file_path, file_hash))
    conn.commit()
    conn.close()

def calculate_file_hash(file_path):
    """Calculates the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def analyze_application(app_id, app_name, source_dir, db_path):
    """Analyzes an application for changes."""
    logging.info(f"Analyzing {app_name} for changes...")
    current_hashes = {}
    for root, _, files in os.walk(source_dir):
        for name in files:
            file_path = Path(root) / name
            relative_path = file_path.relative_to(source_dir)
            current_hashes[str(relative_path)] = calculate_file_hash(file_path)

    stored_hashes = get_file_hashes(app_id, db_path)

    if current_hashes != stored_hashes:
        logging.info(f"Changes detected in {app_name}.")
        update_file_hashes(app_id, current_hashes, db_path)
        return True

    logging.info(f"No changes detected in {app_name}.")
    return False

def package_application(app_id, version, app_name, source_dir, output_dir, db_path):
    """Packages a single application into a .tar.gz archive."""
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_name = f"{app_name}_v{version}.tar.gz"
    archive_path = output_dir / archive_name

    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copytree(source_dir, Path(temp_dir) / app_name)
        logging.info(f"Creating archive for {app_name} at {archive_path}")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(Path(temp_dir) / app_name, arcname=app_name)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET package_path = ?, status = 'packaged' WHERE id = ?", (str(archive_path), app_id))
    conn.commit()
    conn.close()

    logging.info(f"Successfully packaged {app_name} to {archive_path}")

def generate_deployment_plan(app_name, version, config):
    """Generates a markdown template for a deployment plan."""
    plans_dir = Path(config['deployment_plans_directory'])
    plans_dir.mkdir(parents=True, exist_ok=True)

    plan_name = f"{app_name}_v{version}_deployment_plan.md"
    plan_path = plans_dir / plan_name

    content = f"""# Deployment Plan: {app_name} v{version}

**Deployment Date:** YYYY-MM-DD

---

## Pre-Deployment Checklist

- [ ] Backup databases
- [ ] Notify stakeholders
- [ ] Staging environment verified

---

## Deployment Steps

1.  Deploy application to production servers.
2.  Run smoke tests.
3.  Monitor logs and performance metrics.

---

## Rollback Plan

-   Revert to previous version.
-   Restore database from backup if necessary.

---

## Notes

-   Add any relevant notes here.
"""

    with open(plan_path, 'w') as f:
        f.write(content.strip())
    logging.info(f"Generated deployment plan at {plan_path}")

def process_application(app_name, config, db_path):
    """Orchestrates the analysis and packaging of a single application."""
    logging.info(f"--- Processing application: {app_name} ---")

    source_dir = Path(config['apps_directory']) / app_name
    output_dir = Path(config['output_directory'])

    app_id, version, status = get_or_create_app(app_name, db_path)

    has_changed = analyze_application(app_id, app_name, source_dir, db_path)

    if status == 'new':
        logging.info(f"New application {app_name}. Packaging as version {version}.")
        update_app_status(app_id, 'analyzed', db_path, version=version)
        package_application(app_id, version, app_name, source_dir, output_dir, db_path)
        generate_deployment_plan(app_name, version, config)
    elif has_changed:
        version += 1
        logging.info(f"Application {app_name} has changed. Packaging as new version {version}.")
        update_app_status(app_id, 'analyzed', db_path, version=version)
        package_application(app_id, version, app_name, source_dir, output_dir, db_path)
        generate_deployment_plan(app_name, version, config)
    else:
        logging.info(f"Application {app_name} is unchanged. Skipping packaging.")

def main():
    """Main function to run the rep_manager tool."""
    config = load_config('config.yaml')
    log_level = config.get('log_level', 'INFO').upper()
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    db_path = Path(config['database_path'])
    init_db(db_path)

    apps_dir = Path(config['apps_directory'])
    if not apps_dir.exists():
        logging.error(f"Applications directory not found: {apps_dir}")
        return

    for app_dir in sorted(apps_dir.iterdir()):
        if app_dir.is_dir():
            process_application(app_dir.name, config, db_path)

if __name__ == '__main__':
    # Change CWD to the script's directory to make file paths work
    os.chdir(Path(__file__).parent)
    main()
