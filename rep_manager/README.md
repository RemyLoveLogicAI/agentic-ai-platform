# Repository Application Manager (`rep_manager`)

The Repository Application Manager is a Python-based tool for packaging, analyzing, and managing "repository applications". It provides an automated workflow to ensure applications are versioned, archived, and prepared for deployment in a systematic and reliable way.

## Features

-   **Application Packaging:** Automatically packages application source files into versioned `.tar.gz` archives.
-   **Discrepancy Analysis:** Uses SHA256 file hashes to detect changes in application files between runs.
-   **Automatic Versioning:** Increments an application's version number whenever changes are detected.
-   **Persistent Metadata:** Stores application status, version, package paths, and file hashes in an SQLite database for tracking and analysis.
-   **Staging & Archiving:** Uses a temporary staging directory to ensure original files are never modified.
-   **Deployment Plan Generation:** Automatically generates a markdown template for a deployment plan for each new application package.
-   **Configurable:** Uses a `config.yaml` file to allow easy customization of directories and settings.

## Directory Structure

The tool uses the following directory structure within the `rep_manager` folder:

-   `main.py`: The main executable script.
-   `config.yaml`: The configuration file.
-   `apps_to_process/`: Place your applications (as subdirectories) here.
-   `packaged_apps/`: The output directory for the generated `.tar.gz` archives.
-   `deployment_plans/`: The output directory for generated deployment plans.
-   `data/`: Contains the `metadata.db` SQLite database.

## Configuration

The behavior of the script is controlled by the `config.yaml` file:

-   `apps_directory`: The directory containing the applications to be processed.
-   `output_directory`: The directory where packaged archives are stored.
-   `deployment_plans_directory`: The directory where deployment plans are stored.
-   `database_path`: The path to the SQLite database file.
-   `log_level`: The logging level (e.g., INFO, DEBUG).

## Usage

### Prerequisites

You need Python 3 and the `pyyaml` library. Install the dependency using pip:

```bash
pip install pyyaml
```

### Running the tool

To run the manager, execute the `main.py` script. The script is designed to be run from its own directory.

```bash
python3 rep_manager/main.py
```

The script will:
1.  Scan the `apps_to_process` directory for applications.
2.  Analyze each application for changes against the records in the database.
3.  If an application is new or has changed, it will be packaged, its version will be set/incremented, and a deployment plan will be generated.
4.  If an application is unchanged, it will be skipped.
