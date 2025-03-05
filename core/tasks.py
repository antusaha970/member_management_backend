import os
from datetime import datetime
from celery import shared_task
from django.core.management import call_command
import os
from datetime import datetime
from django.core.management import call_command
from celery import shared_task
import psycopg2
from psycopg2 import sql
import os
import subprocess
import datetime
from celery import shared_task
from django.conf import settings
import os
import datetime
import subprocess
from celery import shared_task
import shutil 


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



@shared_task
def backup_postgresql_db():
    print("Backup task started")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    

    # Backup directory
    backup_dir = os.path.join(project_root, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    # Backup file name
    backup_filename = f"pg_db_backup_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.sql"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        # PostgreSQL database connection details
        conn = psycopg2.connect(
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT")
        )
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")

        tables = cur.fetchall()

        for table in tables:
            print(table[0])
        # Backup query to dump PostgreSQL database
        with open(backup_path, "w", encoding="utf-8") as f:
            command = sql.SQL("COPY (SELECT * FROM {} TO STDOUT WITH CSV HEADER)").format(sql.Identifier("member_management_backend"))
            cur.copy_expert(command, f)

        # Close the connection
        cur.close()
        conn.close()

        return f"PostgreSQL backup created: {backup_path}"

    except Exception as e:
        return f"Backup failed: {str(e)}"




# @shared_task
# def backup_database():
#     """
#     Create a backup of the PostgreSQL database using pg_dump and store it in the 'backups' folder.
#     """
#     project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#     backup_dir = os.path.join(project_root, "backups")
#     os.makedirs(backup_dir, exist_ok=True)

#     timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
#     backup_filename = f"backup_{timestamp}.sql.gz"
#     backup_path = os.path.join(backup_dir, backup_filename) 

#     PG_DUMP_PATH = "C:\\Program Files\\PostgreSQL\\16\\bin\\pg_dump.exe"
    
#     command = [
#         PG_DUMP_PATH,
#         "-h", os.environ.get("DB_HOST", "localhost"),
#         "-p", os.environ.get("DB_PORT", "5432"),
#         "-U", os.environ.get("DB_USER"),
#         "-d", os.environ.get("DB_NAME"),
#         "-Fc",  
#         "-f", backup_path  
#     ]

#     env = os.environ.copy()
#     env["PGPASSWORD"] = os.environ.get("DB_PASSWORD", "")

#     try:
#         subprocess.check_call(command, env=env)
#         return f"Backup created successfully: {backup_path}"
#     except subprocess.CalledProcessError as e:
#         print("Error during database backup:", e)
#         raise e
    
    


@shared_task
def backup_database():
    """
    Create a backup of the PostgreSQL database using pg_dump and store it in the 'backups' folder.
    """
    print("generating backup postgresql data")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    backup_dir = os.path.join(project_root, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{timestamp}.sql.gz"
    backup_path = os.path.join(backup_dir, backup_filename)

    PG_DUMP_PATH = os.environ.get("PG_DUMP_PATH").strip('"')


    if not PG_DUMP_PATH:
        raise FileNotFoundError("pg_dump executable not found! Please install PostgreSQL or set pg_dump path manually.")

    command = [
        PG_DUMP_PATH,
        "-h", os.environ.get("DB_HOST", "localhost"),
        "-p", os.environ.get("DB_PORT", "5432"),
        "-U", os.environ.get("DB_USER"),
        "-d", os.environ.get("DB_NAME"),
        "-Fc",  # Compressed backup
        "-f", backup_path  
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = os.environ.get("DB_PASSWORD", "")

    try:
        subprocess.check_call(command, env=env)
        return f"Backup created successfully: {backup_path}"
    except subprocess.CalledProcessError as e:
        print("Error during database backup:", e)
        raise e
