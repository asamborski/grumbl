# views.py

from flask import render_template, request, url_for, session, redirect, g, make_response
from app import app, config_secret 
from requests import request as rq
import requests
import json
import urllib
from flask_pymongo import PyMongo
from app import reviews
import string
# from facebook import get_user_from_cookie, GraphAPI
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

app.config['MONGO_DBNAME'] = 'grumbl'
mongo = PyMongo(app)

BOS_LAT, BOS_LONG  = 42.3601, -71.0589
NY_LAT, NY_LONG = 40.7128, -74.0059

punctuation = string.punctuation

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

	# if info in local DB collection 'food', display info from there 
	resResults_inDB = mongo.db.food.find({"term":term})

	# fix return result format (not just names)
	if resResults_inDB.count() > 0:
		businesses = [entry['resName'] for entry in resResults_inDB] # just returning names for now

		return str(businesses)

	else:
	# otherwise, make API call, store results in DB table(s), and display data as before

		if term == None:
			print("You didn't provide a search term!")
			return json.dumps('')

		## EatStreet API – search for restaurants in city coordinates
		url = "https://api.eatstreet.com/publicapi/v1/restaurant/search"
		querystring = {"latitude":"40.7128","longitude":"-74.0059","method":"both","pickup-radius":"2","search":term}
		headers = {'x-access-token': eatstreet_auth(), 'cache-control': "no-cache" }

		resp = requests.request("GET", url, headers=headers, params=querystring)

		if resp.status_code == 200:
			# return results
			print('Response 200 for restaurant search')

			if len(resp.json()['restaurants']) > 0:
				# print('FOUND 1 OR MORE RESTAURANTS)')
				resResults = []
			
				count = 0
				for res in resp.json()['restaurants']:
		
					if count == 10: break # limit to 10 restaurants

					resKey = res['apiKey']

					## EatStreet API – check for this restaurant's menu
					menuUrl = "https://api.eatstreet.com/publicapi/v1/restaurant/" + str(resKey) + "/menu"
					menuQuery = {"includeCustomizations":"false"}
					menuHeaders = {'x-access-token': eatstreet_auth(), 'cache-control': "no-cache"}

					menuResp = requests.request("GET", menuUrl, headers=menuHeaders, params=menuQuery)

					# If menu exists; if so, this restaurant is an option
					if menuResp.status_code == 200:
						print('Response 200 for menu search')
						
						resName = res["name"]
						resAddress = res["streetAddress"]
						resLogoUrl = res["logoUrl"]
						
						# take out punctuation
						resMenu = [item['name'].lower() for itemGroup in menuResp.json() for item in itemGroup['items']] #,

						# Get this restaurant's Yelp biz id
						yelp_resp = requests.get('https://api.yelp.com/v3/businesses/search',
							params={'location':resAddress, 'radius': 10},
							headers={'Authorization' : "Bearer " + yelp_auth()})

						resStars = None # no Yelp restaurant stars unless rating is found
						resLink = False # no Yelp restaurant link by default unless one is found
						if yelp_resp.status_code == 200:
							print('Response 200 for Yelp search')
							if len(yelp_resp.json()['businesses']) > 0:
								print("FOUND BUSINESS ON YELP!")
								resId = [entry['id'] for entry in yelp_resp.json()['businesses']][0]
								resStars = [entry['rating'] for entry in yelp_resp.json()['businesses']][0]
								resLink = 'https://www.yelp.com/biz/' + resId


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

								restaurantInfo = {"resKey":resKey,
												  "resName":resName,
												  "resAddress":resAddress,
												  "resDish":itemName,
												  'resStars':resStars,
												  #"dishSentiment":dishReviews, 
												  "resLogoUrl":resLogoUrl
												 }

								resResults.append(restaurantInfo)

					else:
						print("The restaurant " + res["name"] + " has no menu available. Moving on.")
						continue

					count += 1

				## CACHE: insert new search term and corresponding results into 'food' collection
				## change mongo schema format
				# mongo.db.food.insert({"term" : term, "result" : resResults})
		
				businesses = [(entry["resDish"], entry["resName"], entry["resStars"], entry['resAddress']) for entry in resResults]

				return str(businesses)

		else:
			print('Response was not 200 (' + str(resp.status_code) + ') for search')
			return json.dumps('')

		return json.dumps(resp.json()) # Other response




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

