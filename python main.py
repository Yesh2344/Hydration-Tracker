import argparse
from datetime import date, timedelta
from utils import DatabaseManager, UnitConverter
import sys

def main():
    """Main function to run the Hydration Tracker application."""

    db_manager = DatabaseManager("hydration.db")
    unit_converter = UnitConverter()

    parser = argparse.ArgumentParser(description="Track your daily water intake.")
    parser.add_argument("action", choices=["log", "daily", "weekly", "unit", "help"], help="Action to perform.")
    parser.add_argument("amount", nargs="?", type=float, help="Amount of water consumed (optional).")
    parser.add_argument("unit", nargs="?", choices=["ml", "oz"], help="Unit of measurement (ml or oz, optional).")

    args = parser.parse_args()

    if args.action == "log":
        if args.amount is None or args.unit is None:
            print("Please provide both amount and unit (ml or oz).")
            sys.exit(1)

        amount_ml = unit_converter.to_ml(args.amount, args.unit)
        db_manager.log_water_intake(date.today(), amount_ml)
        print(f"Logged {args.amount} {args.unit} of water.")

    elif args.action == "daily":
        total_ml = db_manager.get_daily_intake(date.today())
        amount, unit = unit_converter.from_ml(total_ml, db_manager.get_preferred_unit())
        print(f"Total water intake for today: {amount:.2f} {unit}")

    elif args.action == "weekly":
        start_date = date.today() - timedelta(days=6)
        weekly_data = db_manager.get_weekly_intake(start_date, date.today())

        total_weekly_ml = sum(day_data["amount_ml"] for day_data in weekly_data)
        amount, unit = unit_converter.from_ml(total_weekly_ml, db_manager.get_preferred_unit())

        print(f"Total water intake for the past week: {amount:.2f} {unit}")

    elif args.action == "unit":
        if args.unit is None:
            print("Please provide a unit (ml or oz).")
            sys.exit(1)
        db_manager.set_preferred_unit(args.unit)
        print(f"Preferred unit set to {args.unit}.")

    elif args.action == "help":
        parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()