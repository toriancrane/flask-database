from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
import jinja2
import db_methods
import time

app = Flask(__name__)


@app.route('/')
def frontPage():
    """ Front Page Function """
    return render_template('front.html')


@app.route('/restaurants/')
def restaurantsPage():
    """ View All Restaurants Function """
    res_list = db_methods.getAllRestaurants()
    return render_template('restaurants.html', restaurants = res_list)


@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurantPage():
    """ Create New Restaurant Function """
    if request.method == 'POST':
        res_name = request.form['res_name']
        if res_name:
            db_methods.addNewRestaurant(res_name)
            time.sleep(0.1)
            return redirect("/restaurants")
        else:
            error = "You need to enter the name of the restaurant you want to add."
            return render_template('newrestaurant.html', error = error)
    else:
        return render_template('newrestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurantPage(restaurant_id):
    """ Edit Restaurant Function """
    if request.method == 'POST':
        res_name = request.form['res_name']
        if res_name:
            db_methods.editRestaurantName(restaurant_id, res_name)
            time.sleep(0.1)
            return redirect('/restaurants')
        else:
            error = "You need to enter the updated name of the restaurant."
            return render_template("newrestaurant.html", error = error)
    else:
        # Obtain text for name of restaurant
        restaurant = db_methods.searchResByID(restaurant_id)
        res_name = restaurant.name

        # Render edit page with current restaurant name
        return render_template('editrestaurant.html', res_name = res_name)


@app.route('/restaurants/<int:restaurant_id>/delete/')
def deleteRestaurantPage(restaurant_id):
    """ Delete Restaurant Function """
    restaurant = db_methods.searchResByID(restaurant_id)
    res_name = restaurant.name
    error = res_name + " has been deleted from the restaurant database."
    db_methods.deleteRestaurant(restaurant_id)
    return render_template('deleterestaurant.html', error = error)


@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenuPage(restaurant_id):
    """ Show Restaurant Menu Items Function """
    restaurant = db_methods.searchResByID(restaurant_id)
    items = db_methods.getMenuItems(restaurant_id)
    return render_template('menu.html', items = items, restaurant = restaurant)


@app.route('/restaurants/<int:restaurant_id>/menu/new-item/', 
            methods=['GET', 'POST'])
def newMenuItemPage(restaurant_id):
    """ Create New Menu Item Function """
    restaurant = db_methods.searchResByID(restaurant_id)
    res_id = restaurant_id
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_price = request.form['item_price']
        item_desc = request.form['item_desc']
        item_course = request.form['item_course']
        if item_name and item_price and item_desc and item_course:
            db_methods.addNewMenuItem(item_name, item_price, item_desc, item_course, res_id)
            time.sleep(0.1)
            return redirect("/restaurants/%s/menu/" % res_id)
        else:
            error = "Please be sure to fill out all required fields."
            return render_template('newmenuitem.html', error = error)
    else:
        return render_template('newmenuitem.html', res_id = res_id)

# @app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/edit/', 
#             methods=['GET', 'POST'])
# def editMenuItemPage(restaurant_id, item_id):
#     """ Edit Restaurant Function """
#     if request.method == 'POST':
#         item_name = request.form['item_name']
#         item_price = request.form['item_price']
#         item_desc = request.form['item_desc']
#         item_course = request.form['item_course']
#         if item_name and item_price and item_desc:
#             db_methods.editRestaurantName(restaurant_id, res_name)
#             time.sleep(0.1)
#             return redirect('/restaurants/<int:restaurant_id>/menu')
#         else:
#             error = "Please fill out all required fields."
#             return render_template("newrestaurant.html", error = error)
#     else:
#         # Obtain text for item name
#         item_name = db_methods.searchItemNameByID(restaurant_id)

#         # Obtain text for item price

#         # Obtain text for item description

#         # Obtain item course type

#         # Render edit page with current restaurant name
#         return render_template('editmenuitem.html', item_name = item_name,
#                                 item_price = item_price, item_desc = item_desc,
#                                 item_course = item_course)


# @app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
# def restaurantMenuJSON(restaurant_id):
#     restaurant = db_methods.searchResNameByID()
#     items = db_methods.getMenuItems()
#     return jsonify(MenuItems=[i.serialize for i in items])

# @app.route('/restaurants/JSON')
# def restaurantsJSON():
#     restaurants = db_methods.getAllRestaurants()
#     return jsonify(restaurants=[r.serialize for r in restaurants])

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)