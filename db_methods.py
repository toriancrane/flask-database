from flask import flash
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
    flash('New restaurant successfully created!')
    session.commit()

def searchResByID(val):
    restaurant = session.query(Restaurant).filter_by(id = val).one()
    return restaurant

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

def searchItemByID(val):
    item = session.query(MenuItem).filter_by(id = val).one()
    return item

def addNewMenuItem(val1, val2, val3, val4, val5):
    new_item = MenuItem(name = val1, price = val2, description = val3, course = val4, restaurant_id = val5)
    session.add(new_item)
    session.commit()

def editMenuItem(val1, val2, val3, val4, val5):
    item = session.query(MenuItem).filter_by(id = val5).one()
    item.name = val1
    item.price = val2
    item.description = val3
    item.course = val4
    session.add(item)
    session.commit()

def deleteMenuItem(val):
    item = session.query(MenuItem).filter_by(id = val).one()
    session.delete(item)
    session.commit()



# #### Troubleshooting ####
# items = getMenuItems(13)
# for i in items:
#     print i.name, i.price, i.course, i.id

# deleteMenuItem(52)
# for i in items:
#     print i.name, i.price, i.course, i.id