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
- Project Tracker: GitHub Project Board

- Containerized Test: Docker running API and DB servies

- Database: SQL Postgres 

- Front-End UI: HTML and Handlebars with Bootstrap extension

- Test Suite: Mocha used for Unit Tests

- Application Server: Node JS and Flask API server

- Deployable Environment: Render hosting website

- Stock API's: Finnhub for Stock News and Twelve Data for information

## Prerequisities 

There should be no requirements or prior installations to be able to run the website. Render handles all the API keys separately. Use the application link to run the website.

## Running Locally

To run the website locally, you will need both an IDE to open the project on and Docker. First open the project repository:

Note you will need an API keys for Finhubb and Twelve Data

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
[Application Link](https://virtrade-hpue.onrender.com/)