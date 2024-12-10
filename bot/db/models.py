from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
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


class Client(Base):
    __tablename__ = 'clients'
    chat_id = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, default=True)


class CartProducts(Base):
    __tablename__ = 'products_in_cart'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.chat_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)


class FAQ(Base):
    __tablename__ = 'faq'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
