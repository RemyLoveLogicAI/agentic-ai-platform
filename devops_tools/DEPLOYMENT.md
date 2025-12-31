# Application Deployment Guide

This document outlines the general steps required to deploy an application from the `rep_applications.tar.gz` archive.

## Prerequisites

- A target server with a compatible OS (e.g., Linux).
- Necessary runtimes installed (e.g., Python 3.8+, Node.js 14+).
- Access to the server via SSH or other means.
- The `rep_applications.tar.gz` archive.

## Deployment Steps

1.  **Transfer Archive:**
    -   Copy the `rep_applications.tar.gz` archive to the target server.
    -   `scp path/to/rep_applications.tar.gz user@your_server:/path/to/deployment/`

2.  **Extract Archive:**
    -   SSH into the server and navigate to the deployment directory.
    -   Extract the contents of the archive:
        ```bash
        tar -xzvf rep_applications.tar.gz
        ```
    -   This will create directories for each application.

3.  **Install Dependencies:**
    -   Navigate into the specific application's directory you wish to deploy (e.g., `cd app_python_fastapi`).
    -   **For Python applications:**
        ```bash
        pip install -r requirements.txt
        ```
    -   **For Node.js applications:**
        ```bash
        npm install
        ```

4.  **Configure Environment:**
    -   Create an environment file (e.g., `.env`) if required by the application.
    -   Set necessary environment variables such as `PORT`, `DATABASE_URL`, etc.

5.  **Run the Application:**
    -   Use a process manager like `pm2` (for Node.js) or `gunicorn` (for Python) to run the application in the background.
    -   **Python (Gunicorn):**
        ```bash
        gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
        ```
    -   **Node.js (pm2):**
        ```bash
        pm2 start index.js --name "my-app"
        ```

6.  **Verify Deployment:**
    -   Check the logs of the application to ensure it started without errors.
    -   Access the application's URL or IP address in a browser or via `curl` to confirm it is running and responding correctly.
    -   `curl http://localhost:PORT`

## Post-Deployment

- Set up a reverse proxy (e.g., Nginx, Caddy) to handle incoming traffic and manage SSL certificates.
- Monitor the application for performance and errors.
