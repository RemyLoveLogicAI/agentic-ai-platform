# Agentic AI Platform - Application Management System

This repository contains a system for managing, analyzing, and packaging "rep applications" as part of the Agentic AI Platform. It provides a suite of scripts and a structured process to ensure applications are consistent, tracked, and ready for deployment.

## Project Structure

- `applications/`: Contains the individual 'rep applications'. Each application resides in its own subdirectory.
- `scripts/`: Holds the automation scripts for managing the applications.
- `metadata/`: Stores metadata about the applications, including a SQLite database for tracking.
- `packages/`: The output directory for packaged application archives (`.tar.gz`).
- `config.ini`: The central configuration file for the scripts.
- `DEPLOYMENT.md`: Instructions for deploying a packaged application.

## System Components

### 1. Metadata Database

The `metadata/context.db` is an SQLite database that serves as the single source of truth for application status and context. It contains three main tables:
- `applications`: Tracks all registered applications, their paths, and their current status (e.g., `new`, `analyzed`, `packaged`).
- `notes`: A place to store arbitrary notes and context for each application.
- `discrepancies`: Logs the results of the analysis script, highlighting any issues found.

### 2. Configuration

The `config.ini` file allows for easy configuration of the system's directory paths and database name without modifying the scripts.

### 3. Scripts

- `scripts/manage_meta.py`: Initializes the database and syncs the applications from the `applications/` directory. Run this script once to set up the system or whenever you add a new application.
- `scripts/analyze.py`: Performs a discrepancy analysis on a specified application. It checks for common issues (like a missing README) and logs them to the database.
- `scripts/package.sh`: Packages a specified application into a `.tar.gz` archive, ready for deployment.

## Workflow

Here is the typical workflow for managing an application:

1.  **Register a New Application:**
    - Add the new application's files to a new subdirectory in `applications/`.
    - Run the metadata management script to register it in the database:
      ```bash
      python3 scripts/manage_meta.py
      ```

2.  **Analyze the Application:**
    - Run the analysis script on the new application:
      ```bash
      python3 scripts/analyze.py <application_name>
      ```
    - Check the output and the `discrepancies` table in the database for any issues.

3.  **Package the Application:**
    - Once the application is ready, package it using the packaging script:
      ```bash
      ./scripts/package.sh <application_name>
      ```
    - The packaged archive will be saved in the `packages/` directory.

4.  **Deploy the Application:**
    - Follow the instructions in `DEPLOYMENT.md` to deploy the packaged application to your target environment.
