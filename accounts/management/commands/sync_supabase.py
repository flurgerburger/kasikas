import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection


class Command(BaseCommand):
    help = 'Validates Supabase connection, applies migrations, and synchronizes initial films/tickets data'

    def handle(self, *args, **options):
        db_password = os.getenv('DB_PASSWORD')
        if not db_password:
            self.stderr.write(self.style.ERROR(
                "DB_PASSWORD is not set. Please set DB_PASSWORD in your .env file or environment."
            ))
            return

        self.stdout.write("Testing connection to Supabase PostgreSQL...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                row = cursor.fetchone()
                self.stdout.write(self.style.SUCCESS(f"Connected to Supabase! Database: {row[0][:35]}..."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Connection failed: {e}"))
            return

        self.stdout.write("Applying database migrations to Supabase...")
        call_command('migrate')

        self.stdout.write("Synchronizing existing films and seed data...")
        try:
            call_command('loaddata', 'accounts/fixtures/initial_data.json')
            self.stdout.write(self.style.SUCCESS("Successfully loaded existing data fixture into Supabase."))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Fixture notice ({e}), running seed_films command..."))
            call_command('seed_films')

        self.stdout.write(self.style.SUCCESS("Supabase database synchronization complete!"))
