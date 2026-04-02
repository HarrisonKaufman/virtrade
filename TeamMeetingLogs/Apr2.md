## April 2nd Team Meeting

* discussed options for serving webpages
 * may use same flask server that api service is running on
* we now have a python object that represents users
 * discussed how to have it interface with postgres, get current session
* discussed minimum viable product
 * API populates charts properly
 * able to pick what stock youd like to see
 * ability buy/sell
* would like to set up a session authentication protocol
* going to use tradingview for real time/detailed stock info, then the AV/finnhub service for historical and also for "preview" graphs on feed