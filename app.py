from flask import Flask, jsonify, request, Response 
import json
from BookModel import *
from settings import *

import jwt, datetime
from UserModel import User
from functools import wraps

app.config['SECRET_KEY'] = 'meow'

@app.route('/login', methods=['POST'])
def get_token():
	request_data = request.get_json()
	username = str(request_data['username'])
	password = str(request_data['password'])

	match = User.username_password_match(username,password)

	if match:
		expiration_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
		token = jwt.encode({'exp': expiration_date }, app.config['SECRET_KEY'], algorithm = 'HS256')
		return token
	else:
		return Response('',401, mimetype='appication/json')


def token_requred(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		token = request.args.get('token')
		try:
			jwt.decode(token, app.config['SECRET_KEY'])
			return f(*args, **kwargs)
		except:
			return jsonify({'error': 'Need a valid token to view this page'}), 401	
	return wrapper
	


#Get /books/6546984984965161

# post books 
#{
#		"name": "Ana Banana",
#		"price": 6.99,
#		"isbn": 651468498494698
#}

def valid_book_object(book):
	if "isbn" in book and "name" in book and "price" in book:
		return True
	else:
		return False


@app.route('/books', methods=['GET', 'POST'])
@token_requred
def add_book():	
	# If request is GET, just return JSON data of books.
	if request.method == 'GET':
		return jsonify({'books': Book.get_all_books()})
	else:
		# This is part if it is POST request
		request_data = request.get_json()
		if valid_book_object(request_data):
			Book.add_book(request_data['name'], request_data['price'], request_data['isbn'])
			response = Response("",201,mimetype='appication/json')
			response.headers['Location'] = "/books/" + str(request_data['isbn'])
			return response
		else:
			invalidBookObjectErrorMsg = {
				"error": "Invalid book object passed in request",
				"helpString": "Pass data similar to {'isbn':651468498494698,'name:'Biljana Cvetkoska2','price':6.99}"
			}
			response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='appication/json')
			return response


# GET /books/456
@app.route('/books/<int:isbn>')  # second endpoint
def get_book_by_isbn(isbn):
	return_value = Book.get_book_by_isbn(isbn)
	return jsonify(return_value)


#put
@app.route('/books/<int:isbn>', methods=['PUT'])
@token_requred
def replace_book(isbn):
	request_data = request.get_json()
	if(not valid_book_object(request_data)):
		invalidBookObjectErrorMsg = {
			"error": "Invalid book object passed in request",
			"helpString": "Pass data similar to {'isbn':651468498494698,'name:'Biljana Cvetkoska2','price':6.99}"
		}
		response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='appication/json')
		return response
	Book.replace_book(isbn, request_data['name'], request_data['price'])
	response = Response("", status=204, mimetype='appication/json')
	return response


@app.route('/books/<int:isbn>', methods=['PATCH'])
@token_requred
def update_book(isbn):
	request_data = request.get_json()
	updated_book = {}
	if("name" in request_data):
		Book.update_book_name(isbn, request_data['name'])		
	if("price" in request_data):
		Book.update_book_price(isbn, request_data['price'])
	
	response = Response("", status=204)
	response.headers['Location'] = "/books/" + str(isbn)
	return response

		
@app.route('/books/<int:isbn>', methods=['DELETE'])
@token_requred
def  delete_book(isbn):
	if(Book.delete_book(isbn)):
		response = Response("", status=204)
		return response
		
	invalidBookObjectErrorMsg = "The book with the specified isbn number was not found"
	response = Response(json.dumps(invalidBookObjectErrorMsg), status=404, mimetype='appication/json')
	return response

if __name__ == '__main__':
	app.run(port=5000)