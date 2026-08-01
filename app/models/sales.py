from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    price = Column(Integer, default=0)

    ingredients = relationship("MenuIngredient", back_populates="menu")
    transactions = relationship("Transaction", back_populates="menu")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    unit = Column(String(20), nullable=False)

    menus = relationship("MenuIngredient", back_populates="ingredient")


class MenuIngredient(Base):
    __tablename__ = "menu_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Float, nullable=False)

    menu = relationship("Menu", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="menus")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    quantity = Column(Integer, default=0)
    total_price = Column(Integer, default=0)

    menu = relationship("Menu", back_populates="transactions")
