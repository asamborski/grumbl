# views.py

from flask import render_template, request
from app import app
from app import config_secret
import requests
import json
from flask_pymongo import PyMongo
from app import reviews
import string
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Configure database
app.config['MONGO_DBNAME'] = 'grumbl'
#app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/grumbl' ## TODO change MONGO_URI for AWS mongo ##

mongo = PyMongo(app)

BOS_LAT, BOS_LONG  = 42.3601, -71.0589
NY_LAT, NY_LONG = 40.7128, -74.0059 

punctuation = string.punctuation

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
	resResults_inDB = mongo.db.restaurants.find({"term":term})

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

								# Yelp web-scraping for reviews about dish #### TODO: FIX THIS
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

				## CACHE: insert new search term and corresponding restaurant results into collection
				## change mongo schema format
				# mongo.db.restaurants.insert({"term" : term, "result" : resResults})
		
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




