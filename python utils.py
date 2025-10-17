import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from python_dateutil import parser

Base = declarative_base()

class WaterIntake(Base):
    """Represents a record of water intake."""
    __tablename__ = "water_intake"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    amount_ml = Column(Float, nullable=False)

    def __repr__(self):
        return f"<WaterIntake(date='{self.date}', amount_ml={self.amount_ml})>"


class Settings(Base):
    """Represents user settings, such as preferred unit."""
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    preferred_unit = Column(String, default="ml")


class DatabaseManager:
    """Manages the database connection and operations."""

    def __init__(self, db_name):
        self.engine = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self._ensure_settings_exist()

    def _ensure_settings_exist(self):
      """Ensures a settings entry exists, creating it if necessary."""
      if self.session.query(Settings).count() == 0:
        new_settings = Settings()
        self.session.add(new_settings)
        self.session.commit()


    def log_water_intake(self, date, amount_ml):
        """Logs water intake for a given date."""
        existing_record = self.session.query(WaterIntake).filter_by(date=date).first()
        if existing_record:
          existing_record.amount_ml += amount_ml
        else:
          new_intake = WaterIntake(date=date, amount_ml=amount_ml)
          self.session.add(new_intake)
        self.session.commit()


    def get_daily_intake(self, date):
        """Retrieves the total water intake for a specific date."""
        record = self.session.query(WaterIntake).filter_by(date=date).first()
        return record.amount_ml if record else 0.0


    def get_weekly_intake(self, start_date, end_date):
        """Retrieves the water intake for a given week."""
        records = self.session.query(WaterIntake).filter(WaterIntake.date >= start_date, WaterIntake.date <= end_date).all()
        return [{"date": record.date, "amount_ml": record.amount_ml} for record in records]


    def set_preferred_unit(self, unit):
        """Sets the preferred unit of measurement."""
        settings = self.session.query(Settings).first()
        settings.preferred_unit = unit
        self.session.commit()


    def get_preferred_unit(self):
        """Gets the preferred unit of measurement."""
        settings = self.session.query(Settings).first()
        return settings.preferred_unit


class UnitConverter:
    """Converts between different units of measurement."""

    ML_PER_OZ = 29.5735

    def to_ml(self, amount, unit):
        """Converts an amount to milliliters."""
        if unit == "oz":
            return amount * self.ML_PER_OZ
        elif unit == "ml":
            return amount
        else:
            raise ValueError("Invalid unit. Must be 'ml' or 'oz'.")


    def from_ml(self, amount_ml, unit):
        """Converts an amount from milliliters to a given unit."""
        if unit == "oz":
            return amount_ml / self.ML_PER_OZ, "oz"
        elif unit == "ml":
            return amount_ml, "ml"
        else:
            raise ValueError("Invalid unit. Must be 'ml' or 'oz'.")