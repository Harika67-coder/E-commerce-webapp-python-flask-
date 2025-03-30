from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Use SQLite Database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'ecommerce_db.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'another_secret_key'  # For session management

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Home Route - Displays Products
@app.route('/')
def home():
    if 'user' in session:
        products = Product.query.all()
        return render_template('index.html', products=products, user=session['user'])
    return redirect(url_for('login_page'))

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already taken, try another one."
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login_page'))
    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = username
            return redirect(url_for('home'))
        return "Invalid credentials, try again."
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

# Add Product Page
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        new_product = Product(name=name, price=price)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_product.html')

# Initialize the Database with Default Products
def initialize_db():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:  # If no products exist, add default products
            default_products = [
                Product(name="Laptop", price=60000),
                Product(name="Smartphone", price=25000),
                Product(name="Headphones", price=3000),
                Product(name="Smartwatch", price=5000)
            ]
            db.session.add_all(default_products)
            db.session.commit()

if __name__ == '__main__':
    initialize_db()  # Ensure default products are added
    app.run(debug=True)
