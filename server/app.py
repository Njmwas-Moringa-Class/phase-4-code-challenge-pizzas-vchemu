#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask import jsonify
from flask import jsonify, abort
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

#get all restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = []
    for restaurant in restaurants:
        restaurant_dict = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
        restaurant_list.append(restaurant_dict)
    return jsonify(restaurant_list)

#get restaurants with an id
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        restaurant_dict = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [pizza.to_dict() for pizza in restaurant.restaurant_pizzas]
        }
        return jsonify(restaurant_dict)
    else:
        return jsonify({"error": "Restaurant not found"}), 404

#DELETE
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404

#GET /pizzas 
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = []
    for pizza in pizzas:
        pizza_dict = {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        }
        pizza_list.append(pizza_dict)
    return jsonify(pizza_list)

#restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.json

    # Extract data from request
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    # Validate data
    if not all([price, pizza_id, restaurant_id]):
        return jsonify({"errors": ["price, pizza_id, and restaurant_id are required"]}), 400

    try:
        price = int(price)
    except ValueError:
        return jsonify({"errors": ["price must be an integer"]}), 400

    if price <= 0:
        return jsonify({"errors": ["price must be a positive integer"]}), 400

    pizza = Pizza.query.get(pizza_id)
    if not pizza:
        return jsonify({"errors": ["Pizza not found"]}), 404

    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({"errors": ["Restaurant not found"]}), 404

    # Create and add new RestaurantPizza
    restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
    db.session.add(restaurant_pizza)
    db.session.commit()

    # Return response
    return jsonify({
        "id": restaurant_pizza.id,
        "price": restaurant_pizza.price,
        "pizza": restaurant_pizza.pizza.to_dict(),
        "pizza_id": restaurant_pizza.pizza_id,
        "restaurant": restaurant_pizza.restaurant.to_dict(),
        "restaurant_id": restaurant_pizza.restaurant_id
    }), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)