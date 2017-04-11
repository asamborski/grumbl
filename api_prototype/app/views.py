# views.py

from flask import render_template, request
from app import app
from app import config_secret
import requests
import json

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

	if term == None:
		print("You didn't provide a search term!")
		return json.dumps('')

	resp = requests.get('https://api.yelp.com/v3/businesses/search',
		params={'term': term, 'latitude' : BOS_LAT, 'longitude' : BOS_LONG},
		headers={'Authorization' : "Bearer " + yelp_auth()})

	if resp.status_code == 200:
		print('Response 200 for search')
		business_names = [entry['name'] for entry in resp.json()['businesses']]
		str_names = "<br>".join(business_names)
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
