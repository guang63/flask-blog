from flask import Flask, render_template


# Create Flask Instance
app = Flask(__name__)

# Create a route decorator
@app.route('/')

# def index():
#     return "<h1>Hello World!</h1>"

# safe, capitallize, lower, upper, title, trim, striptags

def index():
    first_name = "Guang"
    stuff = "This is <strong>Bold</strong> Text"

    favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
    return render_template("index.html", first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza)
    #striptags prvent hacker from access html 

# localhost:5000/user/guang
@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name=name)

# Create custom Error pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
