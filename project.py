from flask import Flask
import os
import re
import webapp2
import jinja2
import string
import db_methods

app = Flask(__name__)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                            autoescape = True)

#Jinja Methods
def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def render(template, **kw):
    write(render_str(template, **kw))

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    items = db_methods.getMenuItems(restaurant_id)
    render('menu.html', items = items)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)