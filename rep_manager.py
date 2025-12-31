"""
REP Application Management Script
=================================

This script provides a command-line interface for managing REP applications.
It allows for packaging, analysis, progress tracking, and viewing deployment
steps for multiple applications.

The script operates on a directory of applications (`rep_applications/`) and
uses a metadata file (`metadata.json`) to store context and analysis results
for each application without modifying the original files.

Key Features:
-------------
- Package applications into a single .tar.gz archive.
- Analyze applications for discrepancies (e.g., missing files).
- Track the status of each application.
- Store and view deployment steps for each application.
- Keep application files and metadata separate.

Usage:
------
python3 rep_manager.py [command]

Available commands:
  package           Package all applications into a .tar.gz archive.
  analyze           Analyze applications for discrepancies.
  status            Show the current status of all applications.
  deployment-steps  Show the deployment steps for all applications.
"""
import argparse
import json
import logging
import os
import tarfile
from pathlib import Path
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define paths
ROOT_DIR = Path(__file__).parent.resolve()
REP_APPS_DIR = ROOT_DIR / "rep_applications"
METADATA_FILE = ROOT_DIR / "metadata.json"
ARCHIVE_FILE = ROOT_DIR / "rep_applications.tar.gz"

def package_applications():
    """
    Packages the REP applications directory into a .tar.gz archive.
    """
    if not REP_APPS_DIR.exists():
        logging.error(f"Directory not found: {REP_APPS_DIR}")
        return

    logging.info(f"Creating archive: {ARCHIVE_FILE}")
    with tarfile.open(ARCHIVE_FILE, "w:gz") as tar:
        tar.add(REP_APPS_DIR, arcname=os.path.basename(REP_APPS_DIR))
    logging.info("Archive created successfully.")

def analyze_applications():
    """
    Analyzes REP applications for discrepancies and updates metadata.
    """
    if not METADATA_FILE.exists():
        logging.error(f"Metadata file not found: {METADATA_FILE}")
        return

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    logging.info("Starting analysis of REP applications...")
    report = []
    for app_name, app_data in metadata.items():
        app_path = REP_APPS_DIR / app_name
        discrepancies = []

        if not app_path.exists():
            discrepancies.append("Application directory not found.")
        else:
            if not (app_path / "README.md").exists():
                discrepancies.append("Missing README.md")
            if not (app_path / "requirements.txt").exists():
                discrepancies.append("Missing requirements.txt")

        metadata[app_name]["analysis"] = {
            "discrepancies": discrepancies,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        metadata[app_name]["status"] = "analyzed"

        report.append(f"Application: {app_name}")
        if discrepancies:
            report.append("  Discrepancies found:")
            for d in discrepancies:
                report.append(f"    - {d}")
        else:
            report.append("  No discrepancies found.")

    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=4)

    logging.info("Analysis complete. Metadata updated.")
    print("\n--- Analysis Report ---")
    print("\n".join(report))
    print("-----------------------")

def show_status():
    """
    Displays the current status of all REP applications.
    """
    if not METADATA_FILE.exists():
        logging.error(f"Metadata file not found: {METADATA_FILE}")
        return

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    print("\n--- Application Status ---")
    for app_name, app_data in metadata.items():
        print(f"Application: {app_name}")
        print(f"  Status: {app_data.get('status', 'unknown')}")
    print("--------------------------")

def show_deployment_steps():
    """
    Displays the deployment steps for all REP applications.
    """
    if not METADATA_FILE.exists():
        logging.error(f"Metadata file not found: {METADATA_FILE}")
        return

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    print("\n--- Deployment Steps ---")
    for app_name, app_data in metadata.items():
        print(f"Application: {app_name}")
        steps = app_data.get('deployment_steps', [])
        if steps:
            for i, step in enumerate(steps, 1):
                print(f"  {i}. {step}")
        else:
            print("  No deployment steps defined.")
    print("------------------------")

def main():
    """
    Main entry point for the REP application management script.

    This script provides a command-line interface to package, analyze, and
    manage REP applications.
    """
    parser = argparse.ArgumentParser(
        description="A script to manage REP applications for packaging, analysis, and deployment."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # 'package' command
    subparsers.add_parser("package", help="Package the REP applications into a .tar.gz archive.")

    # 'analyze' command
    subparsers.add_parser("analyze", help="Analyze REP applications for discrepancies.")

    # 'status' command
    subparsers.add_parser("status", help="Show the status of REP applications.")

    # 'deployment-steps' command
    subparsers.add_parser("deployment-steps", help="Show the deployment steps for REP applications.")

    args = parser.parse_args()

    if args.command == "package":
        package_applications()
    elif args.command == "analyze":
        analyze_applications()
    elif args.command == "status":
        show_status()
    elif args.command == "deployment-steps":
        show_deployment_steps()

if __name__ == "__main__":
    main()
