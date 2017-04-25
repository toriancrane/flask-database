from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Restaurant, Base, MenuItem
 
engine = create_engine('sqlite:///restaurantmenu.db')
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


#Only query the correct restaurant by id
UrbanVeggieBurger = session.query(MenuItem).filter_by(id = 8).one()
print "Urban Veggie Burger Price: " + UrbanVeggieBurger.price

#Reset price
UrbanVeggieBurger.price = '$2.99'
#Add updated price to session
session.add(UrbanVeggieBurger)
#Commit to database
session.commit()

# #Only query the correct restaurant by id
# print "Urban Veggie Burger Price: " + UrbanVeggieBurger.price

#Change the price of all VeggieBurgers in the database
veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
for veggieBurger in veggieBurgers:
	if veggieBurger.price != '$2.99':
		veggieBurger.price = '$2.99'
		session.add(veggieBurger)
		session.commit()

#Check that it was changed

for veggieBurger in veggieBurgers:
	print veggieBurger.id
	print veggieBurger.price
	print veggieBurger.restaurant.name
	print "\n"