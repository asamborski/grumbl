# views.py

from flask import render_template, request, url_for, session, redirect, g
from app import app, config_secret 
from requests import request as rq
import requests
import json
from flask_pymongo import PyMongo
from facebook import get_user_from_cookie, GraphAPI

# Configure database
app.config['MONGO_DBNAME'] = 'grumbl'
mongo = PyMongo(app)

BOS_LAT = 42.3601
BOS_LONG = -71.0589

#----------------------------------------
# FACEBOOK AUTHENTICATION BELOW
#----------------------------------------

facebook_auth = config_secret.facebook_auth
FB_APP_ID = facebook_auth['client_id']
FB_APP_NAME = facebook_auth['app_name']
FB_APP_SECRET = facebook_auth['client_secret']

# USED WITH LOCAL
oauth_url = 'http://127.0.0.1:5000/oauth_callback'

# USED WITH AWS
hosted_oauth_url = 'http://grumbl.amsamborski.com/oauth_callback'

@app.route('/login')
def login():
	url = 'https://www.facebook.com/v2.9/dialog/oauth?'
	client_id = 'client_id={}'.format(FB_APP_ID)
	redir = '&redirect_uri={}'.format(oauth_url)
	url = url + client_id + redir

	return redirect(url)

@app.route('/oauth_callback')
def parse_token():
	token = request.args.get('code') 

	prefix = 'https://graph.facebook.com/v2.9/oauth/'
	access = 'access_token?client_id={}'.format(FB_APP_ID)
	redir = '&redirect_uri={}'.format(oauth_url)
	secret = '&client_secret={}'.format(FB_APP_SECRET)
	issued_code = '&code={}'.format(token)

	get_access_token = prefix + access + redir + secret + issued_code
 
	response = rq(method="GET", url=get_access_token)
	raw = response.json()

	access_token = raw.get('access_token')
	expires_in = raw.get('expires_in') 
	print('\nAccess token is {}'.format(access_token))
	
	return render_template("index.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

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

