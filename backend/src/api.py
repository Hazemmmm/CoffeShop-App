import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

@app.route('/drinks',methods=['GET'])
def get_all_drinks():
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            abort(404)
            
        drink_short = [drink.short() for drink in drinks]
        
        return jsonify({
            "sucess":True,
            "drinks":drink_short
        })
        
    except:
        abort(404)

@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            abort(404)
            
        drinks_long = [drink.long() for drink in drinks]
        
        return jsonify({
            "sucess":True,
            "drinks":drinks_long
        })
        
    except:
        abort(404)



@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink():
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')
    
    try:
        drink = Drink(title=title,recipe=json.dumps(recipe))
        drink.insert()
    
        return jsonify({
            "success":True,
            "drinks": drink.long()
        })
    except:
        abort(422)


@app.route('/drinks/{id}',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt,id):
    
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
        
    try:
        title = req.get('title')
        recipe = body.get('recipe')
        if title:
            drink.title = title
        if recipe:
            drink.recipe = recipe
        
        drink.update()
        return jsonify({
            "success":True,
            "drinks":[drink.long()]
        })
        
    except:
        abort(400)
    
    
@app.route('/drinks/{id}',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt,id):
    
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    if not drink:
        abort(404)
        
    try:
        drink.delete()
        return jsonify({
            "success":True,
            'delete':id
        })
        
    except:
        abort(400)
    


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success":False,
        "error":400,
        "message":"not found"
    })

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success":False,
        "error":500,
        "message":"server error"
    })

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success":False,
        "error":404,
        "message":"resource not found"
    })

@app.errorhandler(AuthError)
def authorization_error(e):
    response = jsonify(e.error)
    response.status_code = e.status_code
    return response