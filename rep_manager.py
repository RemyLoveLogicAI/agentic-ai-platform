#!/usr/bin/env python3
"""
Repository Application Manager
==============================

A command-line tool for managing repository applications. This tool provides
functionality for packaging, analyzing, and tracking the status of applications.

Commands:
---------
- `package`: Archives application files into a .tar.gz package.
- `analyze`: Compares two application directories and reports discrepancies.
- `status`: Displays the current status and notes for an application.
- `set-status`: Sets the development status of an application.
- `note`: Adds a contextual note to an application.

Usage:
------
    ./rep_manager.py <command> [options]

Examples:
---------
    ./rep_manager.py package --source my_app --output my_app.tar.gz
    ./rep_manager.py analyze --app1 v1.0 --app2 v1.1
    ./rep_manager.py set-status my_app dev
    ./rep_manager.py note my_app "Ready for QA."
    ./rep_manager.py status my_app
"""
import argparse
import filecmp
import json
import logging
import os
import shutil
import sqlite3
import tarfile
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_NAME = "metadata.db"

def handle_package(args):
    """Packages the applications into a tar.gz archive."""
    source_dir = args.source
    output_filename = args.output

    if not os.path.isdir(source_dir):
        logging.error(f"Source directory '{source_dir}' not found.")
        return

    logging.info(f"Packaging applications from '{source_dir}'...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Use a subdirectory within the temp dir to get a clean archive root
        staging_dir = os.path.join(tmpdir, os.path.basename(source_dir))
        shutil.copytree(source_dir, staging_dir)
        logging.info(f"Staged files in temporary directory: {staging_dir}")

        # Here you could do pre-processing on the staged files

        logging.info(f"Creating archive: {output_filename}")
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(staging_dir, arcname=os.path.basename(staging_dir))

    logging.info(f"Successfully created archive '{output_filename}'.")


def handle_analyze(args):
    """Analyzes discrepancies between two application directories."""
    app1_dir = args.app1
    app2_dir = args.app2
    report_filename = "discrepancy_report.md"

    if not os.path.isdir(app1_dir):
        logging.error(f"Directory '{app1_dir}' not found.")
        return
    if not os.path.isdir(app2_dir):
        logging.error(f"Directory '{app2_dir}' not found.")
        return

    logging.info(f"Analyzing discrepancies between '{app1_dir}' and '{app2_dir}'...")

    comparison = filecmp.dircmp(app1_dir, app2_dir)

    with open(report_filename, "w") as f:
        f.write(f"# Discrepancy Report for {os.path.basename(app1_dir)} vs {os.path.basename(app2_dir)}\n\n")

        if comparison.left_only:
            f.write(f"## Files only in {os.path.basename(app1_dir)}\n")
            for item in comparison.left_only:
                f.write(f"- `{item}`\n")
            f.write("\n")

        if comparison.right_only:
            f.write(f"## Files only in {os.path.basename(app2_dir)}\n")
            for item in comparison.right_only:
                f.write(f"- `{item}`\n")
            f.write("\n")

        if comparison.diff_files:
            f.write("## Files with differences\n")
            for item in comparison.diff_files:
                f.write(f"- `{item}`\n")
            f.write("\n")

        if not comparison.left_only and not comparison.right_only and not comparison.diff_files:
            f.write("## No discrepancies found.\n\n")

    logging.info(f"Discrepancy report saved to '{report_filename}'.")


def init_db():
    """Initializes the database and creates tables if they don't exist."""
    con = sqlite3.connect(DB_NAME)
    try:
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'new',
                notes TEXT
            )
        ''')
        con.commit()
    finally:
        con.close()


def handle_status(args):
    """Checks the status and notes of an application."""
    app_id = args.app_id
    con = sqlite3.connect(DB_NAME)
    try:
        cur = con.cursor()
        cur.execute("SELECT status, notes FROM applications WHERE id = ?", (app_id,))
        result = cur.fetchone()
        if result:
            status, notes_json = result
            print(f"Application: {app_id}")
            print(f"Status: {status}")
            notes = json.loads(notes_json) if notes_json else []
            if notes:
                print("Notes:")
                for i, note in enumerate(notes, 1):
                    print(f"  {i}. {note}")
            else:
                print("Notes: None")
        else:
            logging.warning(f"No information found for application '{app_id}'.")
    finally:
        con.close()


def handle_set_status(args):
    """Sets the status for a given application."""
    app_id = args.app_id
    status = args.status
    con = sqlite3.connect(DB_NAME)
    try:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO applications (id) VALUES (?)", (app_id,))
        cur.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
        con.commit()
        logging.info(f"Status for application '{app_id}' set to '{status}'.")
    finally:
        con.close()


def handle_note(args):
    """Adds a note to a given application."""
    app_id = args.app_id
    note_text = args.text
    con = sqlite3.connect(DB_NAME)
    try:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO applications (id) VALUES (?)", (app_id,))
        cur.execute("SELECT notes FROM applications WHERE id = ?", (app_id,))
        result = cur.fetchone()
        current_notes_json = result[0] if result and result[0] else '[]'
        notes = json.loads(current_notes_json)
        notes.append(note_text)
        new_notes_json = json.dumps(notes)
        cur.execute("UPDATE applications SET notes = ? WHERE id = ?", (new_notes_json, app_id))
        con.commit()
        logging.info(f"Added note to application '{app_id}'.")
    finally:
        con.close()


def main():
    """Main function to parse arguments and call handlers."""
    parser = argparse.ArgumentParser(description="Repository Application Manager")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Packaging command
    package_parser = subparsers.add_parser("package", help="Package applications into a tar.gz archive.")
    package_parser.add_argument("--source", default="rep_apps", help="Source directory of applications.")
    package_parser.add_argument("--output", default="rep_applications.tar.gz", help="Output archive file.")
    package_parser.set_defaults(func=handle_package)

    # Analysis command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze discrepancies between applications.")
    analyze_parser.add_argument("--app1", default="rep_apps/app1", help="Path to the first application.")
    analyze_parser.add_argument("--app2", default="rep_apps/app2", help="Path to the second application.")
    analyze_parser.set_defaults(func=handle_analyze)

    # Status command
    status_parser = subparsers.add_parser("status", help="Check the status of an application.")
    status_parser.add_argument("app_id", help="The ID of the application to check.")
    status_parser.set_defaults(func=handle_status)

    # Set-status command
    set_status_parser = subparsers.add_parser("set-status", help="Set the status of an application.")
    set_status_parser.add_argument("app_id", help="The ID of the application.")
    set_status_parser.add_argument("status", help="The new status for the application.")
    set_status_parser.set_defaults(func=handle_set_status)

    # Note command
    note_parser = subparsers.add_parser("note", help="Add a note to an application.")
    note_parser.add_argument("app_id", help="The ID of the application.")
    note_parser.add_argument("text", help="The text of the note to add.")
    note_parser.set_defaults(func=handle_note)

    args = parser.parse_args()
    init_db()  # Initialize DB before running command
    args.func(args)

if __name__ == "__main__":
    main()
