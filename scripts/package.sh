#!/bin/bash

# Exit on error
set -e

# Check for application name argument
if [ -z "$1" ]; then
    echo "Usage: $0 <application_name>"
    exit 1
fi

APP_NAME=$1

# Function to read ini file
# Note: This is a simple parser. It doesn't handle all edge cases of ini files.
get_config() {
    grep "^$2" "$1" | sed "s/$2\s*=\s*//"
}

# Read configuration
CONFIG_FILE="config.ini"
APPS_DIR=$(get_config $CONFIG_FILE "applications_dir")
PACKAGES_DIR=$(get_config $CONFIG_FILE "packages_dir")
DB_FILE=$(get_config $CONFIG_FILE "database")

APP_PATH="$APPS_DIR/$APP_NAME"

# Check if application exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: Application '$APP_NAME' not found in '$APPS_DIR'."
    exit 1
fi

# Create a temporary staging directory
STAGE_DIR=$(mktemp -d)
echo "Staging in: $STAGE_DIR"

# Copy application files to staging directory
cp -r "$APP_PATH" "$STAGE_DIR/"

# Create the package
PACKAGE_NAME="$APP_NAME-$(date +%Y%m%d%H%M%S).tar.gz"
echo "Creating package: $PACKAGE_NAME"
tar -czf "$PACKAGES_DIR/$PACKAGE_NAME" -C "$STAGE_DIR" "$APP_NAME"

# Clean up the staging directory
rm -rf "$STAGE_DIR"

# Update status in the database
echo "Updating status to 'packaged' for '$APP_NAME'"
sqlite3 "$DB_FILE" "UPDATE applications SET status = 'packaged' WHERE name = '$APP_NAME';"

echo "Packaging complete for $APP_NAME."
