import argparse
import json
import logging
import sqlite3
import datetime
from pathlib import Path
import tarfile
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path):
    """Loads the configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}")
        exit(1)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in configuration file at {config_path}")
        exit(1)

def init_database(db_path, apps_dir):
    """Initializes the database and tables if they don't exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create progress table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        app_name TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        last_updated TEXT NOT NULL
    )
    ''')

    # Create notes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        note TEXT NOT NULL,
        FOREIGN KEY (app_name) REFERENCES progress (app_name)
    )
    ''')

    # Discover and add new applications
    apps_dir_path = Path(apps_dir)
    if apps_dir_path.exists() and apps_dir_path.is_dir():
        existing_apps = {row[0] for row in cursor.execute("SELECT app_name FROM progress").fetchall()}
        discovered_apps = {p.name for p in apps_dir_path.iterdir() if p.is_dir()}
        new_apps = discovered_apps - existing_apps

        if new_apps:
            logging.info(f"Discovered new applications: {', '.join(new_apps)}")
            for app_name in new_apps:
                cursor.execute(
                    "INSERT INTO progress (app_name, status, last_updated) VALUES (?, ?, ?)",
                    (app_name, 'NEW', datetime.datetime.now(datetime.timezone.utc).isoformat())
                )

    conn.commit()
    return conn

def handle_status(args, conn):
    """Handles the status command."""
    cursor = conn.cursor()
    if args.app_name:
        cursor.execute("SELECT app_name, status, last_updated FROM progress WHERE app_name = ?", (args.app_name,))
        row = cursor.fetchone()
        if row:
            print(f"Status for {row[0]}: {row[1]} (Last updated: {row[2]})")
        else:
            logging.warning(f"Application '{args.app_name}' not found.")
    else:
        print("Status of all applications:")
        cursor.execute("SELECT app_name, status, last_updated FROM progress ORDER BY app_name")
        for row in cursor.fetchall():
            print(f"- {row[0]:<25} {row[1]:<15} (Last updated: {row[2]})")

def handle_add_note(args, conn):
    """Handles the add-note command."""
    cursor = conn.cursor()
    cursor.execute("SELECT app_name FROM progress WHERE app_name = ?", (args.app_name,))
    if not cursor.fetchone():
        logging.warning(f"Application '{args.app_name}' not found. Cannot add note.")
        return

    cursor.execute(
        "INSERT INTO notes (app_name, timestamp, note) VALUES (?, ?, ?)",
        (args.app_name, datetime.datetime.now(datetime.timezone.utc).isoformat(), args.note)
    )
    conn.commit()
    logging.info(f"Note added to application '{args.app_name}'.")

def handle_show_notes(args, conn):
    """Handles the show-notes command."""
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, note FROM notes WHERE app_name = ? ORDER BY timestamp", (args.app_name,))
    notes = cursor.fetchall()
    if not notes:
        print(f"No notes found for application '{args.app_name}'.")
    else:
        print(f"Notes for {args.app_name}:")
        for row in notes:
            print(f"- [{row[0]}] {row[1]}")

def handle_package(args, conn, config, script_dir):
    """Handles the package command."""
    apps_dir = Path(config['applications_dir'])
    archive_name = script_dir / config['archive_name']

    if not apps_dir.exists() or not any(apps_dir.iterdir()):
        logging.warning("Applications directory is empty or does not exist. Nothing to package.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        staging_dir = Path(tmpdir) / 'staging'

        logging.info(f"Staging applications for packaging...")
        for app_path in apps_dir.iterdir():
            if app_path.is_dir():
                shutil.copytree(app_path, staging_dir / app_path.name)

        logging.info(f"Creating archive: {archive_name}")
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(staging_dir, arcname='.')

        logging.info("Packaging complete.")
        cursor = conn.cursor()
        for app_path in apps_dir.iterdir():
             if app_path.is_dir():
                app_name = app_path.name
                cursor.execute(
                    "UPDATE progress SET status = ?, last_updated = ? WHERE app_name = ?",
                    ('PACKAGED', datetime.datetime.now(datetime.timezone.utc).isoformat(), app_name)
                )
        conn.commit()

def handle_analyze(args, conn, config, script_dir):
    """Handles the analyze command."""
    apps_dir = Path(config['applications_dir'])
    report_path = script_dir / config['report_name']
    analysis_results = {}

    logging.info("Starting discrepancy analysis...")

    for app_path in apps_dir.iterdir():
        if not app_path.is_dir():
            continue

        app_name = app_path.name
        discrepancies = []

        # Check 1: README.md exists
        if not (app_path / 'README.md').exists():
            discrepancies.append("Missing README.md file.")

        # Check 2: Python apps have requirements.txt
        if 'python' in app_name and not (app_path / 'requirements.txt').exists():
            discrepancies.append("Missing requirements.txt file for Python application.")

        analysis_results[app_name] = discrepancies

    # Update database and generate report
    cursor = conn.cursor()
    report_content = ["# Discrepancy Analysis Report\n\n"]

    for app_name, discrepancies in analysis_results.items():
        report_content.append(f"## Application: {app_name}\n\n")
        status = 'ANALYZED_FAIL' if discrepancies else 'ANALYZED_OK'

        if discrepancies:
            report_content.append("**Discrepancies Found:**\n")
            for d in discrepancies:
                report_content.append(f"- {d}\n")
        else:
            report_content.append("No discrepancies found.\n")

        report_content.append("\n")

        cursor.execute(
            "UPDATE progress SET status = ?, last_updated = ? WHERE app_name = ?",
            (status, datetime.datetime.now(datetime.timezone.utc).isoformat(), app_name)
        )

    conn.commit()

    with open(report_path, 'w') as f:
        f.write("".join(report_content))

    logging.info(f"Analysis complete. Report generated at {report_path}")


def main():
    """Main function to parse arguments and call the appropriate command."""
    script_dir = Path(__file__).parent
    config = load_config(script_dir / 'config.json')
    db_path = script_dir / config['database_name']
    apps_dir = Path(config['applications_dir'])

    conn = init_database(db_path, apps_dir)

    parser = argparse.ArgumentParser(description="DevOps tools for managing rep applications.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # 'package' command
    parser_package = subparsers.add_parser('package', help='Package applications into a tar.gz archive.')
    parser_package.set_defaults(func=lambda args: handle_package(args, conn, config, script_dir))

    # 'analyze' command
    parser_analyze = subparsers.add_parser('analyze', help='Analyze applications for discrepancies.')
    parser_analyze.set_defaults(func=lambda args: handle_analyze(args, conn, config, script_dir))

    # 'status' command
    parser_status = subparsers.add_parser('status', help='Check the status of applications.')
    parser_status.add_argument('app_name', nargs='?', default=None, help='The name of the application to check. If not provided, shows status for all apps.')
    parser_status.set_defaults(func=lambda args: handle_status(args, conn))

    # 'add-note' command
    parser_add_note = subparsers.add_parser('add-note', help='Add a note to an application.')
    parser_add_note.add_argument('app_name', help='The name of the application.')
    parser_add_note.add_argument('note', help='The content of the note.')
    parser_add_note.set_defaults(func=lambda args: handle_add_note(args, conn))

    # 'show-notes' command
    parser_show_notes = subparsers.add_parser('show-notes', help='Show notes for an application.')
    parser_show_notes.add_argument('app_name', help='The name of the application.')
    parser_show_notes.set_defaults(func=lambda args: handle_show_notes(args, conn))

    args = parser.parse_args()
    args.func(args)

    conn.close()

if __name__ == "__main__":
    main()
