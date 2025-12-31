# agentic-ai-platform
Agentic AI platform for viral video systems, agent marketplace, onboarding bots, and autonomous marketing.

## Repository Application Management

This project includes a tool, `rep_manager.py`, for managing multiple "repository applications". It helps in packaging, analyzing, and tracking the deployment readiness of applications.

### Features

-   **Package**: Compresses application directories into a `tar.gz` archive.
-   **Analyze**: Performs a discrepancy analysis between two applications and generates a report.
-   **Track Progress**: Uses a local SQLite database (`metadata.db`) to store and track application status and contextual notes.

### Usage

The tool is command-line driven. Here are some examples:

-   **Package all applications:**
    ```bash
    ./rep_manager.py package
    ```

-   **Analyze differences between `app1` and `app2`:**
    ```bash
    ./rep_manager.py analyze
    ```

-   **Set the status of an application:**
    ```bash
    ./rep_manager.py set-status app1 "testing"
    ```

-   **Add a note to an application:**
    ```bash
    ./rep_manager.py note app1 "Passed all integration tests."
    ```

-   **Check the status of an application:**
    ```bash
    ./rep_manager.py status app1
    ```

For more details on the deployment process, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).
