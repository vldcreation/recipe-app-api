"""
Test custom django management commands
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check', return_value=True)
class CommandTest(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db when db is available"""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(database=['default'])

    @patch('time.sleep', return_value=True)
    def test_wait_for_db_delay(self, pathced_sleep,  patched_check):
        """Test waiting for db when getting OperationalError"""
        patched_check.side_effect = [OperationalError] * 2 + \
            [Psycopg2Error] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(database=['default'])




