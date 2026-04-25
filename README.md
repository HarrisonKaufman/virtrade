# Virtrade

## Description

Virtrade is a paper-trading website, which allows you to see the effectiveness of trading techniques and practice them to compete with other users. On the website, you can bet on real stock data using fake money, avoiding the risk of financial loss.

The website supports account creation, stocks news and data, along with a leaderboard to compare your current monetary score.

## Contributors

| Name                     | GitHub Username                  |
|--------------------------|---------------------------------|
| Austin Bushlack          | a-bush6                         |
| Mihai-Alexandru Radu     | MihaiAlexandru-Radu             |
| Dylan Spektor            | spektordylan                    |
| Harrison Kaufman         | HarrisonKaufman                 |
| Ian O’Keefe              | iokee4 / ianokee   |

## Technology Stack

- Project Tracker: GitHub Project Board used to track issues and assign tasks for each member of our team

- Containerized Test: Docker running API and DB servies. When running locally, Docker manages all the network, especially connections between NodeJS and the Postgres data table

- Database: SQL Postgres, featuring tables for user, transactions, etc. 

- Front-End UI: HTML and Handlebars with Bootstrap extension. Each page is its own partial handling both API and Database data when applicable.

- Test Suite: Mocha used for Unit Tests. Test results can be seen when running the website via a Docker container.

- Application Server: NodeJS and Flask API server. Both Node and Flask handle network requests, especially in terms of account and transaction management.

- Deployable Environment: Render hosting website. Has all API keys requiring no further input from the user.

- Stock API's: Finnhub for stock news and Twelve Data for monetary information. Incorporated in both lightweight  and heavy, detailed graphs.

## Directory Structure 

All the project's code resides in `ProjectSourceCode`. 
- `User` holds the user object which primarily hands the partial storing of user monetary information, such as when they buy and sell. This information will ultimately update the database.

- `api` handles API calls of Finnhub and Twelve Data via Flask; it is in charge of rendering the news, buying and selling.
 
- `init_data/create.sql` creates the SQL database which handles everything in terms of storing information, from user info to stock transactions.
 
- `test` runs all unit tests when run locally.
 
- `utils` holds the JSON parser used to put the stock information in a more readable way.
 
- `views` holds all the partials and webpages needed to actually render the website.
 
- `index.js` has every NodeJS method in regards to user information, such as log-in, registration, leaderboard, etc.

## Prerequisities 

There should be no requirements or prior installations to be able to run the website. Render handles all the API keys separately. Use the application link to run the website.

## Running Locally

To run the website locally, you will need both an IDE to open the project on and Docker. First open the project repository:

Note you will need an API keys for Finhubb, Twelve Data, and Postgres environmental variables

1. Go to "ProjectSourceCode" directory
    - From the initial project folder, you can do this via the follwoing command: `cd ProjectSourceCode`

2. Open Docker to ensure you can get it running
3. Type in terminal `docker compose up`

4. You must wait a little than go to `http://localhost:3000/`
    - The link should have the website's login page

## Running Tests

The Unit Tests are ran when you initialize the Docker File. After the command `docker compose up`, wait some time and the tests should run automaticaly.
If working properly this should appear in the terminal:
```
web-1  |   Testing Register API
web-1  |     ✓ positive : /register - should register a new user with valid credentials (62ms)
web-1  |     ✓ negative : /register - should reject registration with invalid email
web-1  |     ✓ negative : /register - should reject missing fields
```

## Deployed Application
Online Website: [Application Link](https://virtrade-hpue.onrender.com/)
