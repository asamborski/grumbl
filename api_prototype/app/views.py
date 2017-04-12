# views.py

from flask import render_template, request
from app import app
from app import config_secret
import requests
import json
from flask_pymongo import PyMongo

# Configure database
app.config['MONGO_DBNAME'] = 'grumbl'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/grumbl' ## TODO change MONGO_URI for AWS mongo ##

mongo = PyMongo(app)

BOS_LAT = 42.3601
BOS_LONG = -71.0589

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
	return render_template("search.html")

@app.route('/', methods=['POST'])
def search_post():
	term = request.form['search-term']

	# if info in local DB, display info from there 
	restaurant_results = mongo.db.restaurants.find({"term":term})

	if restaurant_results.count() > 0:
 		document = [doc for doc in restaurant_results][0]
 		return "<br>".join(document['result'])

	else:
	# otherwise, make API call, store results in DB table(s), and display data as before

		if term == None:
			print("You didn't provide a search term!")
			return json.dumps('')

		## Yelp Search API call and result filtering
		resp = requests.get('https://api.yelp.com/v3/businesses/search',
			params={'term': term, 'latitude' : BOS_LAT, 'longitude' : BOS_LONG, \
					'categories': 'restaurants', 'radius': 3218},
			headers={'Authorization' : "Bearer " + yelp_auth()})

		if resp.status_code == 200:
			print('Response 200 for search')
			business_names = [entry['name'] for entry in resp.json()['businesses']]
			str_names = "<br>".join(business_names)

			# CACHE: insert new search term and corresponding results into collection
			mongo.db.restaurants.insert({"term" : term, "result" : business_names})

			return str_names

		else:
			print('Response was not 200 (%s) for search'.format(resp.status_code))
			return json.dumps('')
		return json.dumps(resp.json())

def yelp_auth():
	resp = requests.post('https://api.yelp.com/oauth2/token', data=config_secret.yelp_auth)

	if resp.status_code == 200:
		return resp.json()['access_token']
	else:
		raise RuntimeError("Couldn't get token. Received status code %s".format(resp.status_code))
