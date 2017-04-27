# get reviews for restaurant on Yelp

from bs4 import BeautifulSoup
import sys
import time
import logging
import argparse
import requests
import codecs
import urllib
import os
import urllib.request
import json

def get_reviews(theurl, foodTerm):
    reviewInfo = {}

    main_page = urllib.request.urlopen(theurl)
    soup = BeautifulSoup(main_page, "html.parser")
    
    review_div = soup.findAll('div',{'itemprop':'review'})

    reviewCount = 1 ## TODO: MUST CHANGE THIS FOR UNIQUE IDs

    for i in review_div: # iterating through review_div 
        # get review star rating
        reviewStar = float(i.find('meta',{'itemprop':'ratingValue'}).get('content', None))

        # get review body text
        reviewBody = i.find('p',{'itemprop':'description'})
        for txt in reviewBody:
            if type(txt) != '<p>' and not str(txt).startswith('<p>'):
                reviewText = txt

        if foodTerm in reviewText: # add review if term in review
	        reviewInfo[reviewCount] = {'review_stars' : reviewStar, \
	                                   'review_text' : reviewText} 
        # else: continue

        reviewCount += 1 ## TODO: MUST CHANGE THIS FOR UNIQUE IDs
        
    return reviewInfo

def getAllReviews(restaurant_url, foodTerm):
    '''Loops though the pages of a restaurant and collects all of its reviews containing specified food term'''

    reviewDict = {}
    reviewCount = 0 ## TODO: MUST CHANGE THIS FOR UNIQUE IDs
    
    stop=0
    while(stop == 0):
    	reviewDict.update(get_reviews(restaurant_url, foodTerm))
    	this_page = urllib.request.urlopen(restaurant_url)
    	soup = BeautifulSoup(this_page, "html.parser")
    	review_div = soup.findAll('link',{'rel':'next'})

    	if len(review_div) != 0:
    		for i in review_div:
    			restaurant_url = i.get('href', None)
    	else:
    		stop = 1 

    	reviewCount += 20 ## TODO: MUST CHANGE THIS FOR UNIQUE IDs

    return reviewDict


##### Main #####
#TestUrl = 'https://www.yelp.com/biz/pavement-coffeehouse-boston'
#print(get_reviews(TestUrl, 'cookie'))
#print(getAllReviews(TestUrl, 'cookie')) 

