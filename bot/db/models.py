from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import Text, DECIMAL
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# SQLAlchemy Models
class ProductCategory(Base):
    __tablename__ = 'product_categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parent_category_id = Column(Integer, nullable=True)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    category_id = Column(Integer, nullable=False)
