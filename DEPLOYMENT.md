# Deployment Procedure for Rep Applications

This document outlines the steps required to package, analyze, and deploy the "rep applications". Following this procedure ensures consistency and technical excellence in the deployment process.

## 1. Pre-deployment: Application Registration and Analysis

Before packaging the applications, it's crucial to ensure that all applications are correctly registered in the metadata database and that there are no discrepancies.

### 1.1. Synchronize Applications with the Database

Run the synchronization script to register any new applications in the metadata database. This step ensures that all applications are tracked.

```bash
python3 scripts/sync_apps_to_db.py
```

### 1.2. Run Discrepancy Analysis

After synchronization, run the analysis script to confirm that there are no outstanding discrepancies. The script should report that the database is in sync.

```bash
python3 scripts/analyze_discrepancies.py
```

### 1.3. Update Application Status (Manual Step)

At this stage, you may want to manually update the status of the applications in the `metadata.db`. For example, you can use a simple script or a database client to update the `status` field for applications that are ready for deployment to `pending_deployment`.

*(Note: A script for status updates can be developed to further automate this process.)*

## 2. Packaging the Applications

Once the applications are verified and their statuses are updated, you can package them into a distributable archive.

Run the packaging script:

```bash
python3 scripts/package_apps.py
```

This will create a new `rep_applications_YYYYMMDD_HHMMSS.tar.gz` file in the `dist/` directory. This archive is the artifact that will be deployed.

## 3. Deployment

The deployment process itself will depend on the target environment. However, the general steps are as follows:

1.  **Transfer the Archive:** Securely transfer the `tar.gz` archive from the `dist/` directory to the target server(s).

2.  **Extract the Archive:** On the target server, extract the contents of the archive.

    ```bash
    tar -xzvf rep_applications_*.tar.gz
    ```

3.  **Configure and Run:** Follow the specific instructions for each application to configure and start them. The extracted directory will contain all the necessary application files.

## 4. Post-deployment: Update Application Status

After a successful deployment, update the status of the deployed applications in the metadata database to `deployed`. This is crucial for progress tracking.

*(Note: This step can also be automated by a script that takes a list of deployed applications as input.)*
