from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, MenuItem, Base

engine = create_engine('sqlite:///restaurantmenu.db?check_same_thread=False')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

def getAllRestaurants():    
    """ Query all of the restaurants and return the results in ascending alphabetical order """
    restaurants = session.query(Restaurant).order_by(Restaurant.name.asc()).all()
    return restaurants

def addNewRestaurant(val):
    new_res = Restaurant(name = val)
    session.add(new_res)
    session.commit()

def searchResNameByID(val):
    restaurant = session.query(Restaurant).filter_by(id = val).one()
    return restaurant.name

def editRestaurantName(val1, val2):
    restaurant = session.query(Restaurant).filter_by(id = val1).one()
    restaurant.name = val2
    session.add(restaurant)
    session.commit()

def deleteRestaurant(val):
    restaurant = session.query(Restaurant).filter_by(id = val).one()
    session.delete(restaurant)
    session.commit()

def getMenuItems(val):
    items = session.query(MenuItem).filter_by(restaurant_id=val)
    return items

def addNewMenuItem(val):
    new_item = MenuItem(name = val)
    session.add(new_item)
    session.commit

#searchRestauarant("Thai Rama")