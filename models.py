from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.String(20)) 

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    owner = db.Column(db.String(100))

    name = db.Column(db.String(200))
    location = db.Column(db.String(200))
    ype = db.Column(db.String(50))   # 🔥 NEW (resort, hall, etc)
    type = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    price_type = db.Column(db.String(50))  # 🔥 per night / per hall
    price = db.Column(db.Float)
    capacity = db.Column(db.Integer)

    services = db.Column(db.String(300))   # catering, decor etc
    image = db.Column(db.String(300))      # image path

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    total_budget = db.Column(db.Float)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    category = db.Column(db.String(100))
    planned_amount = db.Column(db.Float)
    actual_amount = db.Column(db.Float)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user = db.Column(db.String(100))
    venue_id = db.Column(db.Integer)

    rating = db.Column(db.Integer)
    comment = db.Column(db.String(500))

