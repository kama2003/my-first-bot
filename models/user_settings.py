from sqlalchemy import Column, Integer, Float, String, BigInteger
from database.db import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)

    filament_price = Column(Float, default=2500.0)
    filament_weight = Column(Float, default=1000.0)

    electricity_cost = Column(Float, default=8.0)
    printer_power = Column(Float, default=0.12)

    printer_cost = Column(Float, default=65000.0)
    printer_lifetime = Column(Float, default=6000.0)

    defect_percent = Column(Float, default=10.0)
    extra_cost = Column(Float, default=20.0)
    markup_percent = Column(Float, default=150.0)
