import os
from datetime import datetime
from celery import shared_task
from django.core.management import call_command


@shared_task
def backup_sqlite_db():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Backup directory
    backup_dir = os.path.join(project_root, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    # Backup file name
    backup_filename = f"db_backup_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.json"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        # Run Django dumpdata command
        with open(backup_path, "w", encoding="utf-8") as f:
            call_command("dumpdata", indent=2, stdout=f)
        return f"Backup created: {backup_path}"
    except Exception as e:
        return f"Backup failed: {str(e)}"
