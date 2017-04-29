# views.py

from flask import render_template, request, url_for, session, redirect, make_response
from app import app, config_secret 
from requests import request as rq
import requests
import json
import urllib
from flask_pymongo import PyMongo
from app import reviews
import string
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pprint import pprint
import ast

app.config['MONGO_DBNAME'] = 'grumbl'
mongo = PyMongo(app)

BOS_LAT, BOS_LONG  = 42.3601, -71.0589
NY_LAT, NY_LONG = 40.7128, -74.0059

punctuation = string.punctuation

# USED WITH LOCAL
oauth_url = 'http://127.0.0.1:5000/oauth_callback' 


##### Auth Retrieval Functions #####
def yelp_auth():
	'''Yelp API authorization'''
	resp = requests.post('https://api.yelp.com/oauth2/token', data=config_secret.yelp_auth)

	if resp.status_code == 200:
		return resp.json()['access_token']
	else:
		raise RuntimeError("Couldn't get token. Received status code " + str(resp.status_code))


def eatstreet_auth():
	'''EatStreet API authorization'''
	key = config_secret.eatstreet_auth['api-key']
	return key


def facebook_auth():
	# FACEBOOK AUTHENTICATION INFO
	facebook_auth = config_secret.facebook_auth
	FB_APP_ID = facebook_auth['client_id']
	FB_APP_NAME = facebook_auth['app_name']
	FB_APP_SECRET = facebook_auth['client_secret']
	return FB_APP_ID, FB_APP_SECRET, FB_APP_NAME


def eatstreet_api(endpoint, params):
	url = "https://api.eatstreet.com/publicapi"
	headers = {'x-access-token': eatstreet_auth(), 'cache-control': "no-cache"}
	return api(url=url, endpoint=endpoint, params=params, headers=headers)

def yelp_api(endpoint, params, headers):
	url = 'https://api.yelp.com'
	return api(url, endpoint, params, headers)

def fb_api(endpoint, params):
	url = 'https://graph.facebook.com'
	return api(url, endpoint, params)

def api(url, endpoint, params={}, headers={}):
	r = requests.get('%s/%s' % (url, endpoint), params=params, headers=headers)
	if r.status_code == 200:
		print(r.text)
		return r.json()
	else:
		print('%s\n[%d] %s' % (r.url, r.status_code, r.text))
		return None

def respond(path, cookie, **kwargs):
	if cookie is not None:
		result = mongo.db.users.find_one({'fb_id': cookie})
		if result is not None:
			return render_template(path, user=result, **kwargs)
		else:
			return render_template(path, **kwargs)
	else:
		return render_template(path, **kwargs)

@app.route('/')
def index():
	return respond('index.html', request.cookies.get('userID'))
 

@app.route('/login') 
def login():
	FB_APP_ID, FB_APP_SECRET, FB_APP_NAME = facebook_auth()

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
	FB_APP_ID, FB_APP_SECRET, FB_APP_NAME = facebook_auth()

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
		{'$set': {"name" : me['name'], "fb_id" : me['id'], 'access_token': access_token}},  
		upsert=True
		)

	resp = make_response(redirect('/'))
	resp.set_cookie('userID', me['id'])
	return resp


@app.route('/profile')
def profile():
	if request.cookies.get('userID', None) is not None:

		result = mongo.db.users.find_one({'fb_id': request.cookies.get('userID')})

		if result is None:
			return redirect('/login')

		if not 'picture' in result:

			# Get Profile pic
			picture = fb_api('%s/picture' % result.get('fb_id'), params={'type': 'large', 'redirect': False})

			# Stick in DB
			mongo.db.users.update(
				{'_id': result.get('id')}, 
				{'picture': picture['data']['url']}
			)

			# set user object to contain profile
			result['picture'] = picture['data']['url']

		saved = result.get('saved', [])
		wishlist = result.get('wishlist', [])

		return render_template('profile.html', user=result, saved=saved, wishlist=wishlist)

	else: 
		return redirect('/login')


@app.route('/logout')
def logout():
	resp = make_response(redirect('/'))

	# Set cookie back to 0	
	resp.set_cookie('userID', '', expires=0)

	return resp


@app.route('/search')
def search():
	return respond("search.html", request.cookies.get('userID'))


@app.route('/save')
def save():
	cookie = request.cookies.get('userID', None)
	item = request.args.get('item', None)
	item = ast.literal_eval(item)
	if cookie is not None and item is not None and item is not "":
		result = mongo.db.users.find_one_and_update({'fb_id': cookie}, {'$push': {'saved': item}})
		if result is not None:
			return respond('search.html', cookie=cookie, success="Saved!")
		else:
			return respond('search.html', cookie=cookie, error="Unable to save :(")
	else:
		return respond('search.html', cookie=cookie, error="No Item to Save!")


@app.route('/wishlist')
def wishlist():
	cookie = request.cookies.get('userID', None)
	item = request.args.get('item', None)
	item = ast.literal_eval(item)
	if cookie is not None and item is not None and item is not "":
		result = mongo.db.users.find_one_and_update({'fb_id': cookie}, {'$push': {'wishlist': item}})
		if result is not None:
			return respond('search.html', cookie=cookie, success="Added to Wishlist!")
		else:
			return respond('search.html', cookie=cookie, error="Unable to add to wishlist :(")
	else:
		return respond('search.html', cookie=cookie, error="No Item to Add to Wishlist!")

	
@app.route('/results')
def search_post():
	# Make sure the string is converted to lowercase
	term = request.args.get('search-term', None)
	loc = request.args.get('user-loc', None)
	cookie = request.cookies.get('userID', None)

	if term == None:
		print("You didn't provide a search term!")
		return respond('results.html', cookie=cookie)

	# if info in local DB collection 'food', display info from there 
	resResults_inDB = mongo.db.food.find_one({"query": (term, loc)})

	# fix return result format (not just names)
	if resResults_inDB is not None:
		return respond('results.html', cookie=cookie, results=resResults_inDB.get('result'), term=term)

	else:
		# otherwise, make API call, 
		# store results in DB table(s), and display data as before

		## EatStreet API – search for restaurants in city coordinates
		params = {"street-address":loc,"method":"both","pickup-radius":"2","search":term}
		search_resp = eatstreet_api('v1/restaurant/search', params=params)

		if search_resp is None:
			return respond("results.html", cookie=cookie)

		restaurants = search_resp.get('restaurants')

		if len(restaurants) == 0:
			return respond('search.html', cookie=cookie, error="No Results!")

		resResults = []
		count = 0
		for restaurant in restaurants:

			if count == 20: break # limit to 10 restaurants

			resKey = restaurant.get('apiKey')

			## EatStreet API – check for this restaurant's menu
			menu_resp = eatstreet_api(endpoint='v1/restaurant/%s/menu' % str(resKey), params={"includeCustomizations": "false"})

			if menu_resp is None:
				print("The restaurant " + search_resp["name"] + " has no menu available. Moving on.")
				continue

			# If menu exists
			# If so, this restaurant is an option				
			resName = restaurant.get("name")
			address = restaurant.get("streetAddress")
			resLogoUrl = restaurant.get("logoUrl")
			
			# Remove punctuation
			resMenu = [item['name'].lower() for itemGroup in menu_resp for item in itemGroup['items']]

			# Get this restaurant's Yelp biz id
			yelp_resp = yelp_api('v3/businesses/search', params={'location': address, 'radius': 10}, headers={'Authorization' : "Bearer " + yelp_auth()})

			resStars = None # no Yelp restaurant stars unless rating is found
			resLink = False # no Yelp restaurant link by default unless one is found
			resPrice = None # no price by default
			if yelp_resp is not None:
				print('Response 200 for Yelp search')

				businesses = yelp_resp.get('businesses')
				if len(businesses) > 0:
					print("FOUND BUSINESS ON YELP!")
					resId = businesses[0]['id']
					print('resID : ' + str(resId))
					resPrice = businesses[0]['price']
					print('resPrice : ' + str(resPrice))
					resStars = businesses[0]['rating']
					print('resStars : ' + str(resStars))
					resLink = 'https://www.yelp.com/biz/' + resId
					print(resLink)

			# Check menu for term and add restaurant to results if dish is found
			for itemName in resMenu:
				# dishReviews = None # by default, no reviews
				if term in itemName:

					# Yelp web-scraping for reviews about specific food item #### TODO: FIX THIS
					# if resLink:
					# 	print('Searching through reviews for ' + str(term))
					# 	dishReviews = reviews.getAllReviews(resLink, term)
					# 	print('dishReviews: ' + str(dishReviews))
					# 	if dishReviews != {}: print('FOUND REVIEW FOR ' + str(term))

					# Sentiment analysis on reviews about dish
					# sid = SentimentIntensityAnalyzer()

					restaurantInfo = {"resKey": resKey,
									  "resName": resName,
									  "resAddress": address,
									  'resStars': resStars,
									  "resDish": itemName,
									  "resPrice": resPrice,
									  #"resDistance: resDistance",
									  #"dishSentiment":dishReviews, 
									  "resLogoUrl": resLogoUrl
									 }

					resResults.append(restaurantInfo)

			count += 1

		## CACHE: insert new search term and corresponding results into 'food' collection
		## change mongo schema format
		mongo.db.food.insert({"query" : (term, loc), "result" : resResults})

		return respond("results.html", cookie=cookie, results=resResults, term=term)


