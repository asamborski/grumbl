## Sign Up 
As someone who wants to join Grumbl, I want to be able to sign up through the login page by selecting the "New User" option. This link will direct me to a page where I can choose to sign up through Google or Facebook. If I do not have either of those two accounts, I will be directed to the appropriate pages to sign up for either of the two. I can then return to the sign up page of Grumbl to enroll. 

Upon signing up for Grumbl, I will see a page that alerts me that I have successfully joined. I can then navigate to the login page and login with my username and password through whichever service I've chosen (see **Authentication**). 

## Authentication
As a user who is already signed up for Grumbl, I want to be able to login so I can use the service. When I navigate to the login page, I see a prompt to log in with either Facebook or Google. When I enter my username and password, I will be redirected to the home page of Grumbl. If I fail to provide correct authentication information, I will receive an error message and be prompted to try again. 

Login successfully implemented, with try/catch blocks for incorrect user info. Failure to provide correct information redirects user to home page with an error message, where they can attempt to log in again.

## Home Page 
As a logged in user, I want to see the Grumbl home page so that I can find the dish I want to eat. The page will show a search bar where users can input a particular dish (i.e. meatloaf, cheeseburger). After pressing search, the page will display different dishes of the food I have searched for. I can then navigate to pages that feature a particular dish and view more information about it such as address and reviews. 
Home page successfully implemented, containing links to all other important sections of the app. Approach was a healthy mix of features-based and benefits based UI. 

## View Dishes
As a user, I want to be able to see all the information on a certain dish in one place. If I select a specific dish, its corresponding page will show me the restaurant where it is located, a description of the dish, its price, as well as any reviews that have been left previously.

## User Profile
As a user, I want to have a user profile that stores my food preferences and can display my dish lists (see **Lists** in secondary user stories) and dishes I enjoyed previously. When I navigate to my user profile, I will see my username/name as well as my lists, Favorites, and Bookmarks.
## Locating Food: Filtering Options
As a user, when I query a certain dish, I'd like to be able to specify how I'd like the results to be displayed. 

### By Location
I want to be able to filter dishes based on which is closest to me. In this case, I do not care how great the dish itself is, all I care about is getting my hands on that food. The results in this case will be filtered from closest to furthest available locations depending on where I am when I do the search

### By Highest Ratings
I want to eat the very best dish that I've searched for. I do not care if it is far away nor do I care if it's expensive. I want my results to show me the highest rated dish and descending into the lowest ranked dish.

### By Price
I am a user on a budget. I want to eat the dish I have searched for, but I would also like to be mindful of the cost. The results from my search will show in descending order most affordable option to most expensive.

## Lists
As a user, I want to be able to organize dishes into categorized lists. When I navigate to the lists page I will see the lists I've already made, the default "Favorites" list (see **Favorites**) and the option to create a new list. Upon clicking one of my lists, I'll be taken to a page with all of the dishes I added to the list. I can sort these dishes by date added, and the three filtering options listed under **Locating Food: Filtering Options**. 

### Add Dish to List
When I'm browsing through dishes in my search results, I want a simple way to add this dish to one or more of my lists. The "Add to list" button will allow me to choose which list to add the dish to, or to create a new list containing the dish.

### Favorites
As a user, I want a default location to save my favorite dishes without having to make a new list for them. "Favorites" is a pre-made list that I have by default as a user.

#### Favorite a Dish
I want a simple way to add dishes to my Favorites. To add a dish to my Favorites, I press the the heart-shaped Favorite icon next to a dish shown in my search query results. I can navigate to Favorites from my Lists or my User Profile page

## Bookmarks
As a user, I want a place to record dishes I'd like to try or save for later. When I navigate to the Bookmarks page from my User Profile, I will see all the dishes I bookmarked sorted by date. I can also sort this items by the three filtering options listed under **Locating Food: Filtering Options**. 

### Bookmark a Dish
By clicking the bookmark icon next to a dish shown in my search results, I can add a dish to my Bookmarks for future reference.
