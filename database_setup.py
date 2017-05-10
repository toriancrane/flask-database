import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    """ Corresponds to the User table """
    # Table information
    __tablename__ = 'user'

    # Mappers
    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))

class Restaurant(Base):
    """ Corresponds to the restaurant table """
    # Table information
    __tablename__ = 'restaurant'

    # Mappers
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class MenuItem(Base):
    """ Corresponds to the MenuItem table """
    # Table information
    __tablename__ = 'menu_item'

    # Mappers
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

engine = create_engine(
    'sqlite:///restaurantmenuwithusers.db')

Base.metadata.create_all(engine)