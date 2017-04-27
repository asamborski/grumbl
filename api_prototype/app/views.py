# views.py

from flask import render_template, request, url_for, session, redirect, g, make_response
from app import app, config_secret 
from requests import request as rq
import requests
import json
import urllib
from flask_pymongo import PyMongo
from facebook import get_user_from_cookie, GraphAPI

app.config['MONGO_DBNAME'] = 'grumbl'
mongo = PyMongo(app)

# LOCATION
BOS_LAT = 42.3601
BOS_LONG = -71.0589

# FACEBOOK AUTHENTICATION INFO
facebook_auth = config_secret.facebook_auth
FB_APP_ID = facebook_auth['client_id']
FB_APP_NAME = facebook_auth['app_name']
FB_APP_SECRET = facebook_auth['client_secret']

# USED WITH LOCAL
oauth_url = 'http://127.0.0.1:5000/oauth_callback' 

@app.route('/')
def index():
	if request.cookies.get('userID') is not None:

		result = mongo.db.users.find({'id': request.cookies.get('userID')})
		print(result)

		return render_template("index.html", user=result)

	else:
		return render_template('index.html')
 

@app.route('/login') 
def login():
	url = 'https://www.facebook.com/v2.9/dialog/oauth?'

	args = {
		'client_id': FB_APP_ID,
		'redirect_uri': oauth_url
	}

	# Create url with the arguments
	url = url + urllib.parse.urlencode(args)

	return redirect(url)


@app.route('/oauth_callback')
def parse_token():
	token = request.args.get('code') 

	args = {
		'client_id': FB_APP_ID,
		'redirect_uri': oauth_url,
		'client_secret': FB_APP_SECRET,
		'code': token
	}

	r = fb_api('v2.9/oauth/access_token', params=args)

	access_token = r['access_token']
	expires_in = r['expires_in']

	print('Access token is %s' % access_token)
	
	me = fb_api('/v2.5/me', params={'access_token': access_token})

	# Add to DB
	mongo.db.users.update(
		{'fb_id': me['id']}, 
		{"name" : me['name'], "fb_id" : me['id'], 'access_token': access_token},  
		upsert=True
		)

	resp = make_response(redirect('/'))
	resp.set_cookie('userID', me['id'])
	return resp

def fb_api(endpoint, params):
	r = requests.get('https://graph.facebook.com/%s' % endpoint, params=params)
	if r.status_code == 200:
		return r.json()
	else:
		print('[%d] %s' % (r.status_code, r.text))
		return None


@app.route('/logout')
def logout():
	resp = make_response(redirect('/'))
	resp.set_cookie('userID', '', expires=0)
	return resp


@app.route('/search')
def search():
	return render_template("search.html")


@app.route('/results', methods=['POST'])
def search_post():
	term = request.form['search-term']

	# if info in local DB, display info from there 
	restaurant_results = mongo.db.restaurants.find({"term":term})

	if restaurant_results.count() > 0:
		document = [doc for doc in restaurant_results][0]
		print(document['result'])
		return render_template('results.html', results = document['result'])

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

			print(resp.json()['businesses'])

			return render_template('results.html', results = business_names)

		else:
			print('Response was not 200 (%s) for search'.format(resp.status_code))
			return json.dumps('')		
		

def yelp_auth():
	resp = requests.post('https://api.yelp.com/oauth2/token', data=config_secret.yelp_auth)

	if resp.status_code == 200:
		return resp.json()['access_token']
	else:
		raise RuntimeError("Couldn't get token. Received status code %s".format(resp.status_code))

