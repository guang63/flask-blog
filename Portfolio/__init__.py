from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from Portfolio.forms import PostForm, UserForm, NamerForm, PasswordForm, LoginForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid 
import os

# Create Flask Instance
app = Flask(__name__)

# Reduce overhead on Openshift
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Add CK Editor
ckeditor = CKEditor(app)
# Add Database
# sqlite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# MySQL db
app.config['SQLALCHEMY_DATABASE_URI'] = ''

# Secret Key
app.config['SECRET_KEY'] = "You are not suppose to know"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



        

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successfull!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("User Doesn't Exist! - Try Again!")
    return render_template('login.html', form=form)
# Logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for('login'))

# Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id 
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        

        # Check for profile pic
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']


        
            # Grab image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            
            # Save Image
            saver = request.files['profile_pic']
            # Change it to a string to save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("User Updated Successfully!")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update)
            except:
                flash("Error! Looks like there was a problem...try again")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update)
        else:
            db.session.commit()     
            flash("User Updated Successfully!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)

# delete post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 18:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # Deleted Message
            flash("Portfolio Deleted!")
            # Grab all the posts from database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)

        except:
            # Error Message
            flash("Whoops, There was a problem deleting, try again...")

            # Grab all the posts from database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        # Error Message
            flash("You Do Not Have The Authorization!")

            # Grab all the posts from database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)  

@app.route('/posts')
def posts():
    # Grab all the posts from database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.name = form.name.data
        post.profile = form.profile.data
        post.experience = form.experience.data
        post.education = form.education.data
        post.skills = form.skills.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Profile Has Been Updated!")
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.poster_id or current_user.id == 18:
        form.name.data = post.name
        form.profile.data = post.profile
        form.experience.data = post.experience
        form.education.data = post.education
        form.skills.data = post.skills
        return render_template('edit_post.html', form=form)
    else:
        flash("You Do Not Have The Authorization!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('post.html', post=post)

# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(name=form.name.data, profile=form.profile.data, experience=form.experience.data, education=form.education.data, skills=form.skills.data, poster_id=poster)
        # Clear the Form
        form.name.data = ''
        form.profile.data = ''
        form.experience.data = ''
        form.education.data = ''
        form.skills.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)



@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None:
            # Hash the password!   
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, username=form.username.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.password_hash.data = ''
                
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

# Delete
@app.route('/delete/<int:id>')
@login_required
def delete(id):
        if id == current_user.id:
            user_to_delete = Users.query.get_or_404(id)
            name = None
            form = UserForm()

            try:
                db.session.delete(user_to_delete)
                db.session.commit()
                flash("User Deleted Successfully!")
                our_users= Users.query.order_by(Users.date_added)
                return render_template("add_user.html", form=form, name=name, our_users=our_users, id=id)
            
            except:
                flash("There is a problem, try again...")
                return render_template("add_user.html", form=form, name=name, our_users=our_users, id=id)
        else:
            flash("Sorry, you don't have the authorization to delete that user!")
            return redirect(url_for('dashboard'))


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Error! Looks like there was a problem...try again")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)



# Create a route decorator
@app.route('/')
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

# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")

    return render_template("name.html", name=name, form=form)

# # Create Password test Page
# @app.route('/test_pw', methods=['GET', 'POST'])
# def test_pw():
#     username = None
#     password = None
#     user_to_check = None
#     passed = None
#     form = PasswordForm()

#     #Validate Form
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password_hash.data

#         form.username.data = ''
#         form.password_hash.data = ''

#         user_to_check = Users.query.filter_by(username=username).first()
#         # flash("Form Submitted Successfully")
#         # Check Hashed Password
#         passed = check_password_hash(user_to_check.password_hash, password)

#     return render_template("test_pw.html", username=username, password=password, user_to_check=user_to_check, passed=passed, form=form)


# Create a Post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    profile = db.Column(db.Text)
    experience = db.Column(db.Text)
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    # Foreign key to link users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# Create Users Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    # User can have multiple posts
    posts = db.relationship('Posts', backref='poster')
    profile_pic = db.Column(db.String(), nullable=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create String
    def __repr__(self):
	    return '<Name %r>' % self.name
