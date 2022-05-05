# Zaza Goods RESTful API Reference 



---
API Response Formats: 


#### Successful Response

response: { 

	“success”: “true”,

	“data”: “{…payload}”

	

} 


#### Failed Response

error_response: {

	“success”: “false”

	“error” : “<some error message>”

}


### **Dependencies  ** 

[Flask](https://flask.palletsprojects.com/) , [JSON Web Token](https://jwt.io/) , [SQLite](https://www.sqlite.org/) , [SQLAlchemy](https://pypi.org/project/SQLAlchemy/)


---


### Products

---



#### Schema: 

{

id : String , **PRIMARY KEY

name:String ,

description:String , 

price: Integer , 

in_stock: Integer , 

category: String ,

options: String

}

** The category field is used for filtering items and the options are an optional field that corresponds to different product variants ( color , size , etc . . . ) 


#### Routes:

**GET** /api/products/ 

 > returns the list of all products stored in the sqlite database. 

 > payload = […products]

**GET **/api/products/&lt;id>

> params: id ( the id of the desired product)

> payload = &lt; product with matching id > 

**[Restricted] POST** /api/product/create 

> inserts a new product into the sqlite database and then returns the created product if successful. 

> body params : { id , name , description , price , in_stock , category, options } 

> payload = &lt; created product || err > 

**[Restricted] PUT** /api/products/update/&lt;id>

> finds a product with an id matching the &lt;id> param and the updates it with provided data (see req.body)

> req.params = id ( the ID of the product to be updated )

> req.body = any valid product field(s) and new value

> payload = { updated product || err }

	EXAMPLE: updating product with id 123’s name to Bar

	/api/products/update/123 with req.body = { name : “Bar” }


<table>
  <tr>
   <td>request.body: {
<p>
id:String , 
<p>
name:String,
<p>
description:String ,
<p>
price:Integer,
<p>
in_stock:Integer , 
<p>
category:String, 
<p>
options: String, 
<p>
}
   </td>
   <td>request.headers: { 
<p>
	… , zaza_admin_token: <SECRET>  
<p>
} 
<p>
! This key in the header is required for all admin restricted routes. Without it, the requests will fail. 
   </td>
  </tr>
</table>



### Orders

---
#### Schema: 

{

id : String , **PRIMARY KEY

customer: String , 

items: String

subtotal: Integer,

transaction_ref: String

}

** The transaction ref points to the id of the entry in the transaction table associated with that order. 

** customer is the id of the customer who placed the order

** subtotal is stored in cents (ie $10 subtotal ⇒ 1000


#### Routes:

**[RESTRICTED] GET** /api/orders/ 

 > returns the list of all orders stored in the sqlite database. 

 > requires admin key in header 

 > payload = […products]

**GET** /api/orders/<id>

> params: id ( the id of the desired order)

> payload = { order with matching id }


---
### Transaction
---
#### Schema: 
{

id : String , **PRIMARY KEY

customer: String , 

subtotal: Integer,

tax_amt: Integer,

shipp_handlng: Integer,

total: Integer,

}

** customer is the id of the customer who placed the order


#### Routes:

**[RESTRICTED] GET** /api/transactions/ 

 > returns the list of all orders stored in the sqlite database. 

 > requires admin key in header 

 > payload = […products]

**GET** /api/transactions/<id>

> params: id ( the id of the desired order)

> payload = { ...order with matching id }
---
### User
---
#### Schema: 
{

id : String , **PRIMARY KEY

email: String ,

password_hash: String,

addressSaved:String || None,

orders: String

}

** address save option on checkout to set the value. 

** the orders property is a stringified array of orderId’s that the customer has 

#### Routes:

**POST** /api/users/ 

 > a combined route that handles login and register. If new user is 

 > returns the list of all orders stored in the sqlite database. 

 > payload = data: { …createdUser } ||  error: “err”

request.body: { 

	email: String,

	password: String **hashed before save to db

}

**[Login Required] POST** /api/token/

>  calls the User.generate_auth_token function and sends back the token with a 5 minute expire time. 

>  payload = data: {‘token’: &lt;decoded token with 5 minute expiry>} 

**[Login Required] POST** /api/user/

>  gets current logged user’s information ( does not return password hash )

>  payload = data : {...loggedUserNoPW } 


# Zaza Goods GraphQL API Reference 


---

Work in progress . . . 
