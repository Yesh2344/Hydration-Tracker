# Minor edit
import unittest
from unittest.mock import patch
from io import StringIO
import main
import os
import datetime
from utils import DatabaseManager

class TestMain(unittest.TestCase):

    def setUp(self):
        # Use an in-memory database for testing
        self.db_name = "test_hydration.db"
        self.db_manager = DatabaseManager(self.db_name)

        # Patch the main function's DatabaseManager to use the test database
        main.DatabaseManager = lambda db_name: self.db_manager

    def tearDown(self):
        # Clean up the test database after each test
        self.db_manager.session.close()  # Close the session
        engine = self.db_manager.engine
        self.db_manager = None # Ensure it is no longer referenced
        engine.dispose()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)


    def test_log_water_intake(self):
        with patch('sys.argv', ['main.py', 'log', '500', 'ml']):
            main.main()
        today = datetime.date.today()
        intake = self.db_manager.get_daily_intake(today)
        self.assertEqual(intake, 500.0)

    def test_log_water_intake_oz(self):
        with patch('sys.argv', ['main.py', 'log', '16.9', 'oz']): # standard water bottle size
            main.main()
        today = datetime.date.today()
        intake = self.db_manager.get_daily_intake(today)
        self.assertAlmostEqual(intake, 16.9 * 29.5735, places=2)

    def test_daily_intake(self):
        today = datetime.date.today()
        self.db_manager.log_water_intake(today, 750.0)
        with patch('sys.argv', ['main.py', 'daily']), patch('sys.stdout', new_callable=StringIO) as stdout:
            main.main()
        self.assertIn("Total water intake for today: 750.00 ml", stdout.getvalue())

    def test_weekly_intake(self):
        today = datetime.date.today()
        self.db_manager.log_water_intake(today - datetime.timedelta(days=1), 250.0)
        self.db_manager.log_water_intake(today, 500.0)
        with patch('sys.argv', ['main.py', 'weekly']), patch('sys.stdout', new_callable=StringIO) as stdout:
            main.main()
        self.assertIn("Total water intake for the past week: 750.00 ml", stdout.getvalue())

    def test_unit_change(self):
        with patch('sys.argv', ['main.py', 'unit', 'oz']):
            main.main()
        preferred_unit = self.db_manager.get_preferred_unit()
        self.assertEqual(preferred_unit, "oz")

    def test_help_command(self):
        with patch('sys.argv', ['main.py', 'help']), patch('sys.stdout', new_callable=StringIO) as stdout:
            main.main()
        self.assertIn("Track your daily water intake.", stdout.getvalue())


    def test_invalid_unit_with_log(self):
      with patch('sys.argv', ['main.py', 'log', '100', 'invalid']), patch('sys.stdout', new_callable=StringIO) as stdout:
          with self.assertRaises(SystemExit) as context:
              main.main()
          self.assertEqual(context.exception.code, 2)

    def test_missing_amount_and_unit_with_log(self):
      with patch('sys.argv', ['main.py', 'log']), patch('sys.stdout', new_callable=StringIO) as stdout:
          with self.assertRaises(SystemExit) as context:
              main.main()
          self.assertEqual(context.exception.code, 1)
          self.assertIn("Please provide both amount and unit (ml or oz).", stdout.getvalue())

    def test_missing_unit_with_unit(self):
      with patch('sys.argv', ['main.py', 'unit']), patch('sys.stdout', new_callable=StringIO) as stdout:
          with self.assertRaises(SystemExit) as context:
              main.main()
          self.assertEqual(context.exception.code, 1)
          self.assertIn("Please provide a unit (ml or oz).", stdout.getvalue())


if __name__ == '__main__':
    unittest.main()