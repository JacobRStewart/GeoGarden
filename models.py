from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	password = db.Column(db.String(80), nullable=False)
	user_type = db.Column(db.String(64), nullable=False)

	def __init__(self, username, password, user_type):
		self.username = username
		self.password = password
		self.user_type = user_type

	# Format printing
	def __repr__(self):
		return '<User {}>'.format(self.username)

class Garden(db.Model):
  garden_id = db.Column(db.Integer, primary_key=True)
  lat = db.Column(db.Integer, nullable=False)
  lon = db.Column(db.Integer, nullable=False)
  name = db.Column(db.String(24), nullable=False)
  date = db.Column(db.String(24), nullable=False)
  contributor1 = db.Column(db.String(24), default='_')
  contributor2 = db.Column(db.String(24), default='_')
  contributor3 = db.Column(db.String(24), default='_')
	
	# Format printing
def __repr__(self):
  return '<Garden {}>'.format(self.date)