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

@app.route('/restaurants')
def restaurantsPage():
    """ View All Restaurants Function """
    res_list = db_methods.getAllRestaurants()
    return render_template('restaurants.html', restaurants = res_list)

@app.route('/restaurants/new', methods=['GET', 'POST'])
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

@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
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
        res_name = db_methods.searchResNameByID(restaurant_id)

        # Render edit page with current restaurant name
        return render_template('editrestaurant.html', res_name = res_name)

@app.route('/restaurants/<int:restaurant_id>/delete')
def deleteRestaurantPage(restaurant_id):
    """ Delete Restaurant Function """
    res_name = db_methods.searchResNameByID(restaurant_id)
    error = res_name + " has been deleted from the restaurant database."
    db_methods.deleteRestaurant(restaurant_id)
    return render_template('deleterestaurant.html', error = error)


@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    """ Show Restaurant Menu Items Function """
    items = db_methods.getMenuItems(restaurant_id)
    return render_template('menu.html', items = items)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)