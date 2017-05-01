## Sign Up 
As someone who wants to join Grumbl, I want to be able to sign up through the login page by selecting the "New User" option. This link will direct me to a page where I can choose to sign up through Google or Facebook. If I do not have either of those two accounts, I will be directed to the appropriate pages to sign up for either of the two. I can then return to the sign up page of Grumbl to enroll. 

While signing up, I can also input information such as any food preferences. Upon signing up for Grumbl, I will see a page that alerts me that I have successfully joined. I can then navigate to the login page and login with my username and password through whichever service I've chosen (see **Authentication**). 
Successfully implemented ability to create and delete accounts (sign up). Account deletion verifies that the user is signed in. Ability to enter food preferences not implemented as it seemed redundant.

## Authentication
As a user who is already signed up for Grumbl, I want to be able to login so I can use the service. When I navigate to the login page, I see a prompt to log in with either Facebook or Google. When I enter my username and password, I will be redirected to the home page of Grumbl. If I fail to provide correct authentication information, I will receive an error message and be prompted to try again. 

Login successfully implemented, with try/catch blocks for incorrect user info. Failure to provide correct information redirects user to home page with an error message, where they can attempt to log in again.

## Home Page 
As a logged in user, I want to see the Grumbl home page so that I can find the dish I want to eat. The page will show a search bar where users can input a particular dish (i.e. meatloaf, cheeseburger). After pressing search, the page will display different dishes of the food I have searched for. I can then navigate to pages that feature a particular dish and view more information about it such as address and reviews. 
Home page successfully implemented, containing links to all other important sections of the app. Approach was a healthy mix of features-based and benefits based UI. 

## View Dishes
As a user, I want to be able to see all the information on a certain dish in one place. If I select a specific dish, its corresponding page will show me the restaurant where it is located, a description of the dish, its price, as well as any reviews that have been left previously.
Dishes able to be viewed from listing. Location and general price range (from $ to $$$$) available, but specific prices not available from API. Reviews mentioning the dish are available. So, this requirement is basically successfully completed, but it’s worth noting that we were forced to deviate slightly from the spec.

## Review a Dish
As a user, after I have eaten a dish, I want to be able to leave a review so that other users can make decisions on whether or not they want to eat the same dish. If I navigate to the dish's page, I want to see an option to "Leave a Review." When I select this option, I will be navigated to a page where I can write a review with a title and submit it. 
Not implemented because the feature was heavily tied to the sentiment analysis portion. When we realized sentiment analysis caused significant performance cuts, this was also dropped. We may look into this in the future, but without a user base it seemed unnecessary at this point. 

## User Profile
As a user, I want to have a user profile that stores my food preferences and can display my dish lists (see **Lists** in secondary user stories) and dishes I enjoyed previously. When I navigate to my user profile, I will see my username/name as well as my lists, Favorites, and Bookmarks.
Ability to save favorites and bookmarks was added, as well as a wish list and must try list, for added customization, all viewable within the user profile. Profile pic taken from Facebook API. User delete button was implemented, which clears user cookie as well as deletes him or her from Grumbl’s user database. 
## Sentiment Analysis 
As a user viewing a dish with reviews, I want to get a sense for the general consensus or feeling toward this dish. I can do this by looking at the sentiment icon above the dish's reviews. This icon will indicate reviewers' feelings about the dish on a scale of completely negative to completely positive. 
Sentiment analysis, while successfully implemented, was not included or actually instated in the final product as it caused severe performance drops. The decision was made that this was less important to the core function of the app than the loss in performance merited.

## Locating Food: Filtering Options
As a user, when I query a certain dish, I'd like to be able to specify how I'd like the results to be displayed. 
Filtering search results implemented in a variety of ways, including location/distance, ratings, and price. Grumbl verifies that the search is non-empty. 

### By Location
I want to be able to filter dishes based on which is closest to me. In this case, I do not care how great the dish itself is, all I care about is getting my hands on that food. The results in this case will be filtered from closest to furthest available locations depending on where I am when I do the search
Location based search successfully implemented using Google Maps. The results can also be sorted by distance to the user’s current location.

### By Highest Ratings
I want to eat the very best dish that I've searched for. I do not care if it is far away nor do I care if it's expensive. I want my results to show me the highest rated dish and descending into the lowest ranked dish.
Search by rating was successfully implemented via sorting after return from the API. This way users would not fail to see options that may have low ratings purely due to insufficient data. Rating scale is a standard star rating system. Grumbl also allows users to view other people’s reviews that mention a specific dish.

### By Price
I am a user on a budget. I want to eat the dish I have searched for, but I would also like to be mindful of the cost. The results from my search will show in descending order most affordable option to most expensive.
Price based search implemented via a 1-4 scale, represented in $ signs, $ being cheap, $$$$ being expensive. This was done based on the price of the restaurant, rather than the price of the dish, as the restaurant’s general price is more indicative of what you’ll actually end up paying after all the other things that may come with the cost of the primary dish are factored in.

## Lists
As a user, I want to be able to organize dishes into categorized lists. When I navigate to the lists page I will see the lists I've already made, the default "Favorites" list (see **Favorites**) and the option to create a new list. Upon clicking one of my lists, I'll be taken to a page with all of the dishes I added to the list. I can sort these dishes by date added, and the three filtering options listed under **Locating Food: Filtering Options**. 
Favorites successfully implemented, as well as a wish list. Items are able to be added and deleted from lists at user’s request. A notable feature here is duplicates are not checked before it is added to the database; rather, this is left up to the user with the ability to delete an item from the lists.

### Add Dish to List
When I'm browsing through dishes in my search results, I want a simple way to add this dish to one or more of my lists. The "Add to list" button will allow me to choose which list to add the dish to, or to create a new list containing the dish.
Successfully implemented. See above. “list” and “bookmarks” became favorites and wishlist.

### Favorites
As a user, I want a default location to save my favorite dishes without having to make a new list for them. "Favorites" is a pre-made list that I have by default as a user.
Successfully implemented. See above.

#### Favorite a Dish
I want a simple way to add dishes to my Favorites. To add a dish to my Favorites, I press the the heart-shaped Favorite icon next to a dish shown in my search query results. I can navigate to Favorites from my Lists or my User Profile page
Successfully implemented. See above.

## Bookmarks
As a user, I want a place to record dishes I'd like to try or save for later. When I navigate to the Bookmarks page from my User Profile, I will see all the dishes I bookmarked sorted by date. I can also sort this items by the three filtering options listed under **Locating Food: Filtering Options**. 
Bookmarks became the wish list. They are functionally the same, so we consider this a satisfied requirement. We asked corporate just to be sure, and corporate said it’s fine. Also I am corporate. 

### Bookmark a Dish
By clicking the bookmark icon next to a dish shown in my search results, I can add a dish to my Bookmarks for future reference.
Successfully implemented. See above.
