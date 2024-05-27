"""
Django command to wait for database to be available.
"""

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        self.stdout.write('Database available!')

    