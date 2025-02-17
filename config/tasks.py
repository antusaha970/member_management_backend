import os
import subprocess
import datetime
from celery import shared_task
from django.conf import settings


@shared_task
def backup_database():
    """
    Create a backup of the PostgreSQL database using pg_dump and store it.
    """
    # Generate a timestamped filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{timestamp}.sql.gz"

    # Build the pg_dump command. Use environment variables for credentials.
    command = [
        "pg_dump",
        "-h", os.environ.get("DB_HOST", "localhost"),
        "-p", os.environ.get("DB_PORT", "5432"),
        "-U", os.environ.get("DB_USER"),
        "-d", os.environ.get("DB_NAME"),
        "-Fc",  # Use custom format for compressed backups, or use -Z 9 for gzip
        "-f", backup_filename
    ]

    # Set the environment variable for the pg_dump command to use the password
    env = os.environ.copy()
    env["PGPASSWORD"] = os.environ.get("DB_PASSWORD", "")

    try:
        # Run the command and wait for it to finish
        subprocess.check_call(command, env=env)
        # Optionally, upload the backup file to cloud storage (e.g., AWS S3)
        # upload_backup_to_s3(backup_filename)
        # Optionally, delete the local backup file after successful upload
        # os.remove(backup_filename)
        return f"Backup created successfully: {backup_filename}"
    except subprocess.CalledProcessError as e:
        # Log error and re-raise
        print("Error during database backup:", e)
        raise e
