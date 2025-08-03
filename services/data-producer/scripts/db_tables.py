from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func
from sqlalchemy.orm import declarative_base
import os

SALES_TABLE_NAME = os.getenv('SALES_TABLE_NAME', 'rossman_sales')

Base = declarative_base()

class RossmanSalesTable(Base):
    __tablename__ = SALES_TABLE_NAME

    id = Column(Integer, primary_key=True)
    store = Column(Integer, nullable=False)
    dayofweek = Column(Integer)
    date = Column(Date, nullable=False)
    sales = Column(Float)
    customers = Column(Integer)
    open = Column(Integer)
    promo = Column(Integer)
    stateholiday = Column(String(1))
    schoolholiday = Column(Integer)
    productname = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
