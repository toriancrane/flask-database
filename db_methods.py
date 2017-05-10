from flask import flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, MenuItem, Base, User

engine = create_engine('sqlite:///restaurantmenuwithusers.db?check_same_thread=False')
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

def addNewUser(name, email, picture):
    new_user = User(name = name, email = email, picture = picture)
    session.add(new_user)
    session.commit()

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def getUserByResId(res_id):
    restaurant = session.query(Restaurant).filter_by(id = res_id).one()
    return restaurant.user_id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def getAllRestaurants():    
    """ Query all of the restaurants and return the results in ascending alphabetical order """
    restaurants = session.query(Restaurant).order_by(Restaurant.name.asc()).all()
    return restaurants

def addNewRestaurant(name, user_id):
    new_res = Restaurant(name = name, user_id = user_id)
    session.add(new_res)
    session.commit()

def searchResByID(res_id):
    restaurant = session.query(Restaurant).filter_by(id = res_id).one()
    return restaurant

def editRestaurantName(res_id, res_name):
    restaurant = session.query(Restaurant).filter_by(id = res_id).one()
    restaurant.name = res_name
    session.add(restaurant)
    session.commit()

def deleteRestaurant(res_id):
    restaurant = session.query(Restaurant).filter_by(id = res_id).one()
    session.delete(restaurant)
    session.commit()

def getMenuItems(res_id):
    items = session.query(MenuItem).filter_by(restaurant_id=res_id)
    return items

def searchItemByID(item_id):
    item = session.query(MenuItem).filter_by(id = item_id).one()
    return item

def addNewMenuItem(user_id, name, price, desc, course, res_id):
    new_item = MenuItem(user_id = user_id, name = name, price = price,
                description = desc, course = course, restaurant_id = res_id)
    session.add(new_item)
    session.commit()

def editMenuItem(name, price, desc, course, item_id):
    item = session.query(MenuItem).filter_by(id = item_id).one()
    item.name = name
    item.price = price
    item.description = desc
    item.course = course
    session.add(item)
    session.commit()

def deleteMenuItem(item_id):
    item = session.query(MenuItem).filter_by(id = item_id).one()
    session.delete(item)
    session.commit()



# #### Troubleshooting ####
# items = getMenuItems(13)
# for i in items:
#     print i.name, i.price, i.course, i.id

# deleteMenuItem(52)
# for i in items:
#     print i.name, i.price, i.course, i.id