from flask import session as login_session
from functools import wraps
from flask import Flask
from flask import flash
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask import make_response
import random, string
import requests
import jinja2
import httplib2
import db_methods
import time
import os
import json

#Additional imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE = state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = db_methods.getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect/')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['credentials'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:    
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#####   User Login Decorator    #####
def login_required(func):
    """
    A decorator to confirm a user is logged in or redirect as needed.
    """
    @wraps(func)
    def check_login(*args, **kwargs):
        # Redirect to login if user not logged in, else execute func.
        if 'username' not in login_session:
            return redirect('/login')
        else:
            return func(*args, **kwargs)
    return check_login


def createUser(login_session):
    user_name = login_session['username']
    user_email = login_session['email']
    user_pic = login_session['picture']
    db_methods.addNewUser(user_name, user_email, user_pic)
    
    user_id = db_methods.getUserID(user_email)
    return user_id


@app.route('/')
def frontPage():
    """ Front Page Function """
    if 'username' not in login_session:
        return render_template('front.html')
    else:
        user_id = login_session['user_id']
        return render_template('front.html', user_id = user_id)


@app.route('/restaurants/')
def restaurantsPage():
    """ View All Restaurants Function """
    res_list = db_methods.getAllRestaurants()
    if 'username' not in login_session:
        return render_template('publicrestaurants.html', restaurants = res_list)
    else:
        user_id = login_session['user_id']
        return render_template('restaurants.html', restaurants = res_list,
                                user_id = user_id)


@app.route('/restaurants/new/', methods=['GET', 'POST'])
@login_required
def newRestaurantPage():
    """ Create New Restaurant Function """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        res_name = request.form['res_name']
        user_id = login_session['user_id']
        if res_name:
            db_methods.addNewRestaurant(res_name, user_id)
            time.sleep(0.1)
            return redirect("/restaurants")
        else:
            error = "You need to enter the name of the restaurant you want to add."
            return render_template('newrestaurant.html', error = error)
    else:
        return render_template('newrestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
@login_required
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
@login_required
def deleteRestaurantPage(restaurant_id):
    """ Delete Restaurant Function """
    restaurant = db_methods.searchResByID(restaurant_id)
    if 'username' not in login_session:
        return redirect('/login')
    else:
        res_name = restaurant.name
        error = res_name + " has been deleted from the restaurant database."
        db_methods.deleteRestaurant(restaurant_id)
        return render_template('deleterestaurant.html', error = error)


@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenuPage(restaurant_id):
    """ Show Restaurant Menu Items Function """
    restaurant = db_methods.searchResByID(restaurant_id)
    items = db_methods.getMenuItems(restaurant_id)
    creator = db_methods.getUserByResId(restaurant_id)
    if 'username' not in login_session or creator != login_session['user_id']:
        return render_template('publicmenu.html', items = items, 
                                restaurant = restaurant, creator = creator)
    else:
        user_id = login_session['user_id']
        return render_template('menu.html', items = items, restaurant = restaurant, 
                                creator = creator, user_id = user_id)


@app.route('/restaurants/<int:restaurant_id>/menu/new-item/', 
            methods=['GET', 'POST'])
# @login_required
def newMenuItemPage(restaurant_id):
    """ Create New Menu Item Function """
    restaurant = db_methods.searchResByID(restaurant_id)
    res_id = restaurant_id
    user_id = login_session['user_id']
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_price = request.form['item_price']
        item_desc = request.form['item_desc']
        item_course = request.form['item_course']
        if item_name and item_price and item_desc and item_course:
            db_methods.addNewMenuItem(user_id, item_name, item_price, 
                                    item_desc, item_course, res_id)
            time.sleep(0.1)
            return redirect("/restaurants/%s/menu/" % res_id)
        else:
            error = "Please be sure to fill out all required fields."
            return render_template('newmenuitem.html', error = error)
    else:
        return render_template('newmenuitem.html', res_id = res_id)

@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/edit/', 
            methods=['GET', 'POST'])
# @login_required
def editMenuItemPage(restaurant_id, item_id):
    """ Edit Menu Item Function """
    item = db_methods.searchItemByID(item_id)
    res_id = restaurant_id
    item_id = item_id
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_price = request.form['item_price']
        item_desc = request.form['item_desc']
        item_course = request.form['item_course']
        if item_name and item_price and item_desc and item_course:
            db_methods.editMenuItem(item_name, item_price, item_desc, item_course, item_id)
            time.sleep(0.1)
            return redirect('/restaurants/%s/menu' % res_id)
        else:
            error = "Please fill out all required fields."
            return render_template("editmenuitem.html", error = error)
    else:
        return render_template('editmenuitem.html', item=item, res_id=res_id)

@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/delete/')
# @login_required
def deleteMenuItemPage(restaurant_id, item_id):
    """ Delete Menu Item Function """
    item = db_methods.searchItemByID(item_id)
    res_id = item.restaurant_id
    error = item.name + " has been deleted from the restaurant menu."
    db_methods.deleteMenuItem(item_id)
    return render_template('deleteitem.html', error = error, res_id = res_id, 
                            item = item)

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
    app.secret_key = 'gDI1tL5OC54UiTF3g18a-bWg'
    app.debug = True
    app.run(host = '0.0.0.0', port = int(os.environ.get('PORT', 33507)))