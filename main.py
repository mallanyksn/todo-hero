from flask import Flask, render_template, url_for, abort, redirect, abort, session, request, flash, get_flashed_messages
# to store users to a database
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
# To login and logout the users
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
# To generate the default image
from flask_gravatar import Gravatar
# For Hashing the passwords
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
# to load thee environment variables
from dotenv import load_dotenv
# loading the forms
from forms import ContactForm
# to access environment variables
from os import getenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')

default_gravatar = Gravatar(app,
                            size=100,
                            rating='g',
                            default='retro',
                            force_default=False,
                            force_lower=False,
                            use_ssl=False,
                            base_url=None)
date = datetime.datetime.now().strftime('%d/%m/%Y')

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure the user-loader
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('unauthorized.html')

# Tables
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    profile_pic = db.Column(db.String(250))

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(250), nullable=False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(100))
    date = db.Column(db.String(100))

class RandomThoughts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thought = db.Column(db.String(100))



db.create_all()  # Creating the tables

# Routes

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            login_user(user)
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('home'))
    return render_template('index.html', current_user=current_user)


@app.route('/homepage', methods=['POST', 'GET'])
def home():
    contact_form = ContactForm()
    todos = Todo.query.all()
    deleted = History.query.all()
    thoughts = RandomThoughts.query.all()
    return render_template('homepage.html',
                           contact_form=contact_form,
                           current_user=current_user,
                           todos=todos,
                           date=date,
                           deleted_todos=deleted,
                           thoughts=thoughts)


@app.route('/account')
def account():
    return render_template('account.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    find_user = User.query.filter_by(
        email=request.form.get('registeremail')).first()
    if find_user == None:
        password = generate_password_hash(request.form.get(
            'registerpassword'), method='pbkdf2:sha256', salt_length=13)
        new_user = User(
            name=request.form.get('username'),
            email=request.form.get('registeremail'),
            password=password,

        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        login_user(new_user)
        return redirect(url_for('home'))
    else:
        flash('There is already an account with that email.')
        return redirect(url_for('account'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    find_user = User.query.filter_by(
        email=request.form.get('loginemail')).first()
    if find_user == None:
        flash('You need to register an account to login.')
        return redirect(url_for('account'))
    elif check_password_hash(find_user.password, request.form.get('password')):
        session['user_id'] = find_user.id
        login_user(find_user)
        return redirect(url_for('home'))
    else:
        flash('You have the wrong password.')
        return redirect(url_for('home'))


@app.route('/my-profile')
@login_required
def profile():
    return render_template('profile.html', gravatar=default_gravatar, current_user=current_user)


@app.route('/add-todo', methods=['POST', 'GET'])
def add_todo():
    todo = request.form.get('todo')
    new_todo = Todo(
        todo=todo)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete/<int:todoid>')
def delete(todoid):
    todo = Todo.query.filter_by(id=todoid).first()
    date_deleted = datetime.datetime.now().strftime('%d/%m/%Y')
    deleted = History(
        todo=todo.todo,
        date=date_deleted)
    db.session.add(deleted)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<int:todoid>', methods=['POST', 'GET'])
def edit(todoid):
    todo = Todo.query.filter_by(id=todoid).first()
    return redirect(url_for('home'))


@app.route('/add-thought/', methods=['POST', 'GET'])
def add_thought():
    new_thought = RandomThoughts(thought=request.form.get('thought'))
    db.session.add(new_thought)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete-thought', methods=['POST', 'GET'])
def delete_all_thoughts():
    all_thoughts = RandomThoughts.query.all()
    for thought in all_thoughts:
        db.session.delete(thought)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/update_profile', methods=['POST', 'GET'])
def update_profile():
    return redirect(url_for('profile'))


@app.route('/clear-history')
def clear_history():
    history = History.query.all()
    for history_item in history:
        db.session.delete(history_item)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/edit-preferences',methods=['POST','GET'])
def edit_preferences():
    email_notification = request.form.get('emailnotification')
    public = request.form.get('public')
    num_todos = request.form.get('numtodos')
    print(email_notification)
    password(public)
    print(num_todos)
    return redirect(url_for('profile'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=8000)
