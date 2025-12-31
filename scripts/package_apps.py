import os
import shutil
import tarfile
import tempfile
import datetime
import yaml

def load_config(root_dir):
    """Loads the configuration from config.yaml."""
    config_path = os.path.join(root_dir, "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def package_applications(apps_dir, dist_dir, archive_basename):
    """
    Packages applications from a source directory into a TAR.GZ archive.

    This function creates a temporary staging directory, copies the applications
    to it, and then creates a compressed TAR.GZ archive in the destination
    directory.

    Args:
        apps_dir (str): The path to the directory containing the applications.
        dist_dir (str): The path to the directory where the archive will be saved.
        archive_basename (str): The base name for the output archive.
    """
    if not os.path.isdir(apps_dir):
        print(f"Error: Application directory not found at '{apps_dir}'")
        return

    if not os.listdir(apps_dir):
        print(f"Warning: Application directory '{apps_dir}' is empty. No archive will be created.")
        return

    # Create a temporary staging directory
    with tempfile.TemporaryDirectory() as staging_dir:
        print(f"Created temporary staging directory: {staging_dir}")

        # Copy applications to the staging directory
        for item in os.listdir(apps_dir):
            s = os.path.join(apps_dir, item)
            d = os.path.join(staging_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks=True)
            else:
                shutil.copy2(s, d)

        print(f"Copied applications to staging directory.")

        # Create the TAR.GZ archive
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{archive_basename}_{timestamp}.tar.gz"
        archive_path = os.path.join(dist_dir, archive_name)

        print(f"Creating archive: {archive_path}")
        with tarfile.open(archive_path, "w:gz") as tar:
            for item in os.listdir(staging_dir):
                tar.add(os.path.join(staging_dir, item), arcname=item)

        print(f"Successfully created archive: {archive_path}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_config(project_root)

    paths = config['paths']
    packaging_config = config['packaging']

    apps_directory = os.path.join(project_root, paths['applications'])
    dist_directory = os.path.join(project_root, paths['distribution'])
    archive_basename = packaging_config['archive_basename']

    # Create dist directory if it doesn't exist
    if not os.path.exists(dist_directory):
        os.makedirs(dist_directory)

    package_applications(apps_directory, dist_directory, archive_basename)
