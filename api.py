#!/Users/blaze/.local/share/virtualenvs/blaze-uj87hD20/bin

import json
import sys
import os
import time
from unicodedata import category
from uuid import uuid4
from flask import Flask, abort, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, false, true
from sqlalchemy.dialects.sqlite import insert
from flask_httpauth import HTTPBasicAuth
import jwt
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash

from utilities import get_attrs, respond_fail, respond

MINUTE = 60

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS']='Content-Type'
app.config["SECRET_KEY"] = 'the quick brown fox'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
@app.route("/")
def hello():
    return jsonify({"msg":"hello"})

#extensions
db = SQLAlchemy(app)

auth = HTTPBasicAuth()

class Order( db.Model ): 
    __tablename__ = "orders"
    id=db.Column(db.String , primary_key=True)
    customer=db.Column(db.String) #customer user id
    items=db.Column(db.String) # stringified array of items in order
    subtotal=db.Column(db.Integer) 
    transaction_ref=db.Column(db.String) #transaction id
    def jsonified(self) -> str:
        return "{" + f"'id':'{self.id}', 'customer': '{self.customer}', 'subtotal':{self.subtotal}, 'transaction_ref':{self.transaction_ref} , 'items':'[{self.items}]'"  + "}"

class Transaction( db.Model ): 
    __tablename__ = "transactions" 
    id=db.Column(db.String, primary_key=True)
    customer=db.Column( db.String(16) )#customer uid
    subtotal=db.Column( db.Integer)
    tax_amt=db.Column( db.Integer) 
    shipp_handling=db.Column( db.Integer) 
    total=db.Column( db.Integer) 
    def jsonified(self): 
        return "{" + f"'id':'{self.id}', 'customer': '{self.customer}', 'subtotal':{self.subtotal}, 'shipp_handling':{self.shipp_handling}, 'tax_amt':{self.tax_amt}, 'total':{self.total}"  + "}"

class Product( db.Model ): 
    __tablename__ = "products"
    id=db.Column(db.String, primary_key=True)
    name=db.Column(db.String)
    description=db.Column(db.String)
    price=db.Column(db.Integer)
    in_stock=db.Column(db.Integer)
    category=db.Column(db.String) 
    options=db.Column(db.String) #stringified list of options
    def jsonified(self):
        return  "{" +f"'id':'{self.id}', 'name':'{self.name}' , 'description':'{self.description}' , 'price':{self.price} , 'in_stock':{self.in_stock}, 'category':'{self.category}', 'options': '[{self.options}]'" + "}" 
          
        
   
class User( db.Model ):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    orders=db.Column(db.String)
    address_saved=db.Column(db.String)
    def jsonified(self):
        return "{" + f"'id':'{self.id}' , 'email','{self.email}' , 'orders':'{self.orders}'"
    
    def add_order(self , order_ref ) -> bool:
        listy = list(self.orders.split(","))
        og_len = len(listy)
        listy.insert(0,order_ref)
        new_len = len(listy)
        if new_len - og_len == 1:
            self.orders = ",".join(listy)
            db.session.commit()
            return True
        else: 
            print("Error adding order to list. ")
            return False



    def hashword(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self , password ): 
        return check_password_hash(self.password_hash , password )

    def generate_auth_token(self , expires_in=600):
        enc = { 'id': self.id,'exp': time.time()+expires_in}
        return jwt.encode( payload=enc , key=app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token( token ): 
        try: 
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])

@auth.verify_password
def verify_password(email_or_token, password):
    #first try token
    user = User.verify_auth_token(email_or_token)
    if not user:
        #try to authenticate email and password
        user = User.query.filter_by(email=email_or_token).first()
        if not user: 
            return False
        if not user.verify_password(password):
            return False

        #set "g" (global) user to match if auth passes
        g.user = user
        return True

@app.route("/api/users", methods=["POST"])
def user_landing():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None: 
        abort(400) # missing arguments
    user = User.query.filter_by(email=email).first()
    if user is not None:
        # existing user check if password matches
        if verify_password( email , password=password):
            g.user = user
            return (respond({
                "email": user.email,
                "status": "registered",
                "token": user.generate_auth_token(600)
            }) , 201 )
    else:
        print("Creating a user")
        #generate unique id , create user with email
        user = User(id=(str(uuid4())), email=email )    
        if not user: 
            return (respond_fail("Failed to create user"), 500)
        user.hashword(password=password) #hash password before saving
        #save to db 
        db.session.add(user)
        db.session.commit()
        return (respond({
            "email": user.email,
            "status": "registered",
            "token": user.generate_auth_token(600)
        }) , 201)

    

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': (5 * MINUTE)})


@app.route('/api/user_details')
@auth.login_required
def get_user():
    if g.user is None : 
        return respond_fail("No error logged in. Unauthorized")
    else:
        return respond(g.user.jsonified())



"""
API/PRODUCTS
__public__:
- get_products
    @route: /api/products [GET]
    data payload is a list of all products in the SQLite DB
- get_product
    @route: /api/products/{id} [GET]
    data payload is a single product matching the "id" param 

__ADMIN__:
- create_product
? params { id , name , description , price, in_stock }
@ route: /api/products/create [POST]
  creates a new product entry in the SQLite DB. 
  data payload is the newly created "product" 



-
"""
@app.route('/api/products', methods=["GET"])
def get_products():
    products = Product.query.all()
    if not products:
        return respond_fail("No products found"), 404 
    return respond([product.jsonified() for product in products])

@app.route('/api/products/<id>')
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return respond_fail(f"No product found with id: {id}"), 404 
    return respond(product.jsonified())




# STORE ADMIN ONLY 
# TODO: add an admin checker to routes ( maybe have a specific header? )

@app.route('/api/products/create' , methods=["POST"])
def create_product( ):
    #get attrs from body
    p = get_attrs(
        "id,name,description,price,in_stock,category,options",
         request.json 
    )

    #create product 
    product = Product(
        id=p['id'],
        name=p['name'],
        description=p['description'],
        price=p['price'],
        in_stock=p['in_stock'], 
        category=p["category"] , 
        options=p["options"]
    )
    
    if product is None:
        return respond_fail("Failed to create product") , 500

    #insert to db 
    db.session.add(product)
    db.session.commit()

    #respond w/ created product
    return respond(product.jsonified())


@app.route('/api/products/update/<int:id>', methods=["PUT"])
def update_product( id ):
    to_update = Product.query.get(id)
    if to_update is None: 
        return respond(f"No product found with id: {id}") , 404 
    keys = ["name , description , price , in_stock"]
    
    for k in keys: 
        to_update[k] = request.json.get(k)
    
    db.session.commit()
    return respond(to_update)



@app.route('/api/orders/')
def get_orders():
    orders = Order.query.all()
    if not orders: return respond_fail("no orders found") , 404
    return respond([order.jsonified() for order in orders ])

@app.route('/api/orders/<id>')  
def get_order(id):
    order = Order.query.get(id)
    if not order: abort(404) #no order found
    return respond(order)

@app.route('/api/orders/delete/<id>')
def delete_order(id):
    order = Order.query.get(id)
    if not order: 
        return respond_fail(f"No order found with id {id}") , 404
    #delete from table
    db.session.delete(order)

    #commit change
    db.session.commit()
    return respond(f"Deleted order with id {id}")


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)  


    