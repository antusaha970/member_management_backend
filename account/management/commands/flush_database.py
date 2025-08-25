from django.core.management.base import BaseCommand
from django.db import connections, transaction, DatabaseError
import sys

class Command(BaseCommand):
    help = 'Flush all data from the secondary database safely'

    # Optional: tables to skip during flush
    SKIP_TABLES = ['django_migrations', 'sqlite_sequence']

    def handle(self, *args, **options):
        db_alias = 'secondary'  # Target DB
        connection = connections[db_alias]

        self.stdout.write(self.style.NOTICE(f"Starting flush of database '{db_alias}'..."))

        try:
            with transaction.atomic(using=db_alias):
                with connection.cursor() as cursor:
                    # Disable foreign key checks for SQLite
                    cursor.execute("PRAGMA foreign_keys = OFF;")

                    # Get all table names
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [t[0] for t in cursor.fetchall()]

                    if not tables:
                        self.stdout.write(self.style.WARNING("No tables found in the database."))
                        return

                    for table_name in tables:
                        if table_name in self.SKIP_TABLES:
                            self.stdout.write(f"Skipping table: {table_name}")
                            continue
                        cursor.execute(f'DELETE FROM "{table_name}";')
                        self.stdout.write(f"Flushed table: {table_name}")

                    # Re-enable foreign key checks
                    cursor.execute("PRAGMA foreign_keys = ON;")

            self.stdout.write(self.style.SUCCESS(f"Secondary database '{db_alias}' flushed successfully!"))

        except DatabaseError as e:
            self.stderr.write(self.style.ERROR(f"Database error occurred: {e}"))
            sys.exit(1)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error: {e}"))
            sys.exit(1)
