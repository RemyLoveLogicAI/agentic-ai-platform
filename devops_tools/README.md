# DevOps Management Tools

This directory contains a suite of tools for managing "rep applications". The central tool is `manager.py`, a Python script that provides a command-line interface for packaging, analyzing, and tracking the applications.

## System Components

-   **`manager.py`**: The main CLI script.
-   **`config.json`**: Configuration file for the manager script.
-   **`metadata.db`**: An SQLite database that stores application status and contextual notes.
-   **`DEPLOYMENT.md`**: A guide for deploying applications.
-   **`discrepancy_report.md`**: An auto-generated report from the `analyze` command.
-   **`rep_applications.tar.gz`**: An auto-generated archive from the `package` command.

## Prerequisites

-   Python 3.7+
-   Required Python packages can be installed if needed, but the script currently uses only the standard library.

## Usage

All commands should be run from the root of the repository.

### View Application Status

To see the status of all applications:
```bash
python3 devops_tools/manager.py status
```

To see the status of a specific application:
```bash
python3 devops_tools/manager.py status app_python_fastapi
```

### Analyze Applications

To run a discrepancy analysis on all applications:
```bash
python3 devops_tools/manager.py analyze
```
This command checks for common issues (like missing `README.md` files) and generates a `discrepancy_report.md`. It also updates the application status in the database.

### Package Applications

To package all applications into a single `tar.gz` archive:
```bash
python3 devops_tools/manager.py package
```
This creates `rep_applications.tar.gz` in the `devops_tools` directory and updates the application status to `PACKAGED`.

### Manage Notes

To add a contextual note to an application:
```bash
python3 devops_tools/manager.py add-note <app_name> "<your note here>"
```
Example:
```bash
python3 devops_tools/manager.py add-note app_nodejs_express "Ready for initial testing."
```

To view all notes for an application:
```bash
python3 devops_tools/manager.py show-notes <app_name>
```
Example:
```bash
python3 devops_tools/manager.py show-notes app_nodejs_express
```
