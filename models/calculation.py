from sqlalchemy import Column, Integer, Float, String, BigInteger, DateTime
from sqlalchemy.sql import func
from database.db import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    material = Column(String(20), default="PLA")
    weight = Column(Float)
    print_time = Column(Float)
    copies = Column(Integer, default=1)
    infill = Column(Float, default=100.0)

    cost_filament = Column(Float)
    cost_electricity = Column(Float)
    cost_amortization = Column(Float)
    cost_extra = Column(Float)
    cost_defect = Column(Float)
    cost_delivery = Column(Float, default=0.0)
    cost_packaging = Column(Float, default=0.0)
    cost_postprocess = Column(Float, default=0.0)
    cost_painting = Column(Float, default=0.0)
    cost_assembly = Column(Float, default=0.0)
    desired_profit = Column(Float, default=0.0)

    total_cost = Column(Float)
    sale_price = Column(Float)
