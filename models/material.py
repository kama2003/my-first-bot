from sqlalchemy import Column, Integer, Float, String, BigInteger
from database.db import Base


MATERIAL_NAMES = ["PLA", "PETG", "ABS", "TPU", "ASA", "Nylon"]


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    name = Column(String(20), nullable=False)
    filament_price = Column(Float, default=2500.0)
    filament_weight = Column(Float, default=1000.0)
