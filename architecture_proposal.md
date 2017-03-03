
# User Login

![Login](/img/login.png)

Note: User has no previous session or session has expired


## User Story Steps (Login with Facebook)

### Happy Path
1. User navigates to the Grumbl Login page
2. User presses button to opt to login via Facebook
3.
  * User is redirected to Facebook for authentication
  * User logs in using their username and password
  * Facebook returns a valid session state (session = ‘connected’)
4. Session expiration and other relevant information is stored in association with that user in the user table
5. User is redirected with the valid session to their Grumbl home page

### Bad Paths
1. User does not click the login button
  * No action taken
2. User does not have a Facebook account
  * Facebook will prompt user to create an account on its own login page
3. User’s connection drops mid-login
  * Request will timeout
  * Facebook will return an error response
  * User will be directed to Facebook login yet again and repeat the process of logging in
4. Facebook website is down
  * User is displayed with login button if they return to Grumbl login page
  * We cannot control Facebook’s servers 
  * If repeated failure, may display an apology message to user letting them know Facebook is down
5. User is not successfully redirected to homepage
  * Reconfiguration of redirect URI may be necessary
  * Addendum: we do not expect this behavior
6. Session information (expiration time etc.) is not stored
  * We repeat write to database
  * Repeated failure: log errors 

### Architecture and Platform Choices
#### Back-end: Python with Flask
We would like to use Python in conjunction with a Flask web framework and MongoDB database to develop our web application. As a team, we are all familiar with Python as a programming language and have had some exposure to MongoDB. Despite our lack of experience with MongoDB, we know that the two pair well together especially with the available Python libraries we can integrate to facilitate Mongo connections as well as to make REST calls.

Compared to other Python web frameworks (e.g. Django), Flask is lightweight and flexible. We don’t require the plethora of features of full-stack web frameworks and don’t want to be limited by their rigidity. Flask makes routing URLs easy and supports a variety of extensions to add functionalities such as database integration, authentication, and form validation. It also comes with built-in debugging tools which should help with app testing.

Lastly, we believe that these tools will allow us to focus primarily on adding more features and functionality to our application rather than struggling to do the basics such as establish a database connection.

We have decided to use AngularJS on the front-end, supported by our MongoDB and Python back-end. As a team, we are comfortable working in Python and would like to expand our knowledge by learning about a noSQL database (Mongo) and a JavaScript frontend. By choosing a language that we are familiar with as the backend, we can spend more time developing our skills with the database and frontend. 

#### Database: Mongo
MongoDB allows you to store information in JSON (JavaScript Object Notation) format (more flexible than a relational SQL database). Therefore Mongo is a format that JavaScript already understands. Furthermore, since MongoDB naturally responds in a format that’s understood by Angular, the code needed to manipulate encoded data is dramatically reduced. 

#### Front-end: Angular
Angular is an open-source JavaScript framework, and simplifies development by using an MVC structure, making it highly testable and reusable. Despite lacking experience in both Angular and Mongo, there is plenty of support for these tools (Mongo is the most popular noSQL database, whilst Angular is well maintained by Google)


### Alternative Architecture and Platform Choices

An alternative platform considered was Node.js and Express.js on the server side. Ultimately, this architecture would be a poor choice for our application for the following reasons:

#### Node.js & Express.js
Node utilizes an asynchronous model (non blocking I/O) - making it too reliant on multiple callbacks (which can prevent other requests from being serviced depending on how much time it takes). This means the application could waste large amounts of time retrieving vital data for the user e.g. restaurant information. Node’s need for nested callbacks produces messy code, making documentation and maintenance difficult. Furthermore, the Grumbl application needs to maintain a significant portion of its state, hence Node’s asynchronous schema is inappropriate for the application’s needs.
Additionally, Node’s API also updates and rolls back on certain features at frequent intervals. This means specific aspects of the application could break/malfunction depending on version of Node being used. This instability/inconsistency makes Node unable to reliably satisfy all the application’s requirements.

