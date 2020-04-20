import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import or_, and_

# DB model
from models import db, User, Garden

app = Flask(__name__)

# DB config
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'gardens.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'development key'
app.config.from_object(__name__)
db.init_app(app)

# Define initdb
@app.cli.command('initdb')
def initdb_command():
  db.drop_all()
  db.create_all()
  db.session.add(User(username='admin', password='hunter2', user_type='admin'))
  db.session.add(Garden(name='one', date='today', lat='39.952583', lon='-75.165222'))
  db.session.add(Garden(name='two', date='today', lat='40.440624', lon='-79.9959'))
  db.session.commit()
  print(User.query.all())
  print(Garden.query.all())
  print('Initialized the database.')

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()

# Getter functions
def get_user_id(username):
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

def get_all_gardens():
	rv = Garden.query.order_by(Garden.date).all()
	return rv if rv else [] 

def get_contributor_gardens(user_id):
	rv = Garden.query.filter(or_(Garden.contributor1==user_id, Garden.contributor2==user_id, Garden.contributor3==user_id))
	return rv if rv else []

def get_contributor_openings(user_id):
	rv = Garden.query.filter(~get_contributor_gardens(user_id))

def check_availabilty(date):
	rv = Garden.query.filter_by(date=date).first()
	return rv if rv else None

def format_datetime(timestamp):
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')
  
@app.route('/pin')
def pin():
	return render_template('pin.html')
  
@app.route('/garden')
def viewGarden():
	return render_template('garden.html')
  
@app.route('/about')
def about():
	return render_template('about.html')
  
@app.route("/getMarkers", methods=['GET', 'POST'])   
def get_markers():
    rv = Garden.query.all()
    d = {}
    i = 0
    for row in rv:
      t =(row.lat, row.lon, row.name)
      d[i]=t
      i+= 1
    return d
    
@app.route("/getData", methods=['GET', 'POST'])   
def get_marker_data():
    rv = Garden.query.filter(and_(Garden.lat == request.form['lati'], Garden.lon == request.form['lngi']))
    di = {}
    j = 0
    for row in rv:
      ti =(row.name, row.lon, row.lat, row.date)
      di[j]=ti
      j+= 1
    return di

@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user:
		return redirect(url_for('profile'))
	error = None
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username.'
		elif user.password != request.form['password']:
			error = 'Invalid password.'
		else:
			flash('Successfully logged in!')
			session['user_id'] = user.user_id
			session['user_type'] = user.user_type
			return redirect(url_for('profile'))
	return render_template('login.html', error=error)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
	
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'Please enter a username.'
		elif not request.form['password']:
			error = 'Please enter a password.'
		elif request.form['password'] != request.form['password2']:
			error = 'Passwords do not match.'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(request.form['username'], request.form['password'], user_type='contributor'))
			db.session.commit()
			flash('Successfully registered new contributor.')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

@app.route('/logout')
def logout():
	flash('You are now logged out.')
	session.pop('user_id', None)
	return redirect(url_for('index'))

# Display user profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
	openings = None
	if g.user.user_type == 'owner':
		gardens = get_all_gardens()
	elif g.user.user_type == 'admin':
		gardens = get_admin_gardens(g.user.user_id)
	else:
		gardens = get_contributor_gardens(g.user.username)
		openings = get_all_gardens() # i sort through this in profile
	return render_template('profile.html', gardens=gardens, openings=openings)	

# Admin garden routes
@app.route('/add_garden', methods=['POST'])
def add_garden():
  if check_availabilty(request.form['date']):
    flash("/////////")
  else:
    db.session.add(Garden(name=request.form['name'], date=request.form['date'], lat=request.form['lat'], lon=request.form['lng']))
    db.session.commit()
    flash('Garden created.')
  return render_template('garden.html')

@app.route('/delete_garden', methods=['POST'])
def delete_garden():
	db.session.delete(Garden.query.filter_by(garden_id=request.form['garden_id']).first())
	db.session.commit()
	return redirect(url_for('profile'))

@app.route('/sign_up1', methods=['POST'])
def sign_up1():
	temp = Garden.query.filter_by(garden_id=request.form['garden_id']).first()
	temp.contributor1 = request.form['contributor1']
	db.session.commit()
	return redirect(url_for('profile'))

@app.route('/sign_up2', methods=['POST'])
def sign_up2():
	temp = Garden.query.filter_by(garden_id=request.form['garden_id']).first()
	temp.contributor2 = request.form['contributor2']
	db.session.commit()
	return redirect(url_for('profile'))

@app.route('/sign_up3', methods=['POST'])
def sign_up3():
	temp = Garden.query.filter_by(garden_id=request.form['garden_id']).first()
	temp.contributor3 = request.form['contributor3']
	db.session.commit()
	return redirect(url_for('profile'))

app.jinja_env.filters['datetimeformat'] = format_datetime