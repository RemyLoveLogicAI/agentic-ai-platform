# Deployment Guide

This document provides a general template for deploying the repository applications.

## Pre-deployment Checklist

1.  **Run Discrepancy Analysis**: Ensure there are no unexpected differences between the application to be deployed and the reference version.
    ```bash
    ./rep_manager.py analyze --app1 <reference_app> --app2 <deploy_app>
    ```
2.  **Check Application Status**: Verify the application is in the correct state (e.g., 'qa-approved') before deploying.
    ```bash
    ./rep_manager.py status <deploy_app>
    ```
3.  **Create Production Package**: Package the final application code.
    ```bash
    ./rep_manager.py package --source rep_apps/<deploy_app> --output <deploy_app>.tar.gz
    ```

## Deployment Steps

1.  **Transfer Package**: Securely transfer the `<deploy_app>.tar.gz` archive to the production server.
    ```bash
    scp <deploy_app>.tar.gz user@production-server:/path/to/deployment/
    ```
2.  **Connect to Server**: SSH into the production server.
    ```bash
    ssh user@production-server
    ```
3.  **Deploy Application**:
    - Stop the current running version of the application.
    - Back up the old application directory.
    - Extract the new package.
    - Install dependencies.
    - Start the new version of the application.
4.  **Post-deployment Verification**:
    - Check application logs for any startup errors.
    - Run health checks or smoke tests.
    - Monitor the application for a while.
5.  **Update Status**: Once deployment is verified, update the application's status.
    ```bash
    ./rep_manager.py set-status <deploy_app> prod
    ./rep_manager.py note <deploy_app> "Deployed to production on $(date)"
    ```
