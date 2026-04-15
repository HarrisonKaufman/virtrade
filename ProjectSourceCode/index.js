// *****************************************************
// <!-- Section 1 : Import Dependencies -->
// *****************************************************

const express = require('express'); // To build an application server or API
const app = express();
const handlebars = require('express-handlebars'); //to enable express to work with handlebars
const Handlebars = require('handlebars'); // to include the templating engine responsible for compiling templates
const path = require('path');
const pgp = require('pg-promise')(); // To connect to the Postgres DB from the node server
const bodyParser = require('body-parser');
const session = require('express-session'); // To set the session object. To store or access session data, use the `req.session`, which is (generally) serialized as JSON by the store.
const bcrypt = require('bcryptjs'); //  To hash passwords
const axios = require('axios'); // To make HTTP requests from our server. We'll learn more about it in Part C.
const bcryptjs = require('bcryptjs');

// *****************************************************
// <!-- Section 2 : Connect to DB -->
// *****************************************************

// create `ExpressHandlebars` instance and configure the layouts and partials dir.
const hbs = handlebars.create({
  extname: 'hbs',
  layoutsDir: __dirname + '/views/layouts',
  partialsDir: __dirname + '/views/partials',
  // add json helper to parse json data in chart partial
  helpers: {
    json: (context) => JSON.stringify(context),
    eq: (a, b) => a == b,
    add: (a , b) => a + b
  }
});

// database configuration
const dbConfig = {
  host: 'db', // the database server
  port: 5432, // the database port
  database: process.env.POSTGRES_DB, // the database name
  user: process.env.POSTGRES_USER, // the user account to connect with
  password: process.env.POSTGRES_PASSWORD, // the password of the user account
};

const db = pgp(dbConfig);

// *****************************************************
// <!-- Section 3 : App Settings -->
// *****************************************************

// Register `hbs` as our view engine using its bound `engine()` function.
app.engine('hbs', hbs.engine);
app.set('view engine', 'hbs');
app.set('views', path.join(__dirname, 'views'));
app.use(bodyParser.json()); // specify the usage of JSON for parsing request body.

// initialize session variables
app.use(
  session({
    secret: process.env.SESSION_SECRET,
    saveUninitialized: false,
    resave: false,
  })
);

app.use(
  bodyParser.urlencoded({
    extended: true,
  })
);

// *****************************************************
// <!-- Section 4 : API Routes & Middleware -->
// *****************************************************

// Auth middleware
const auth = (req, res, next) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  next();
};

app.get('/', (req, res) => {
  res.render('pages/login');
});

app.get('/home', auth, async (req, res) => {
  try {
    const user = await db.one(
      `SELECT username, email, balance, is_active
       FROM users
       WHERE id = $1`,
      [req.session.user]
    );

    const symbols = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'GOOGL', 'MSFT', 'META', 'NFLX'];

    const newsResults = await Promise.all(
      symbols.map(symbol => getCachedNews(symbol))
    );

    const newsData = {};
    symbols.forEach((symbol, i) => {
      newsData[symbol] = newsResults[i].articles || [];
    });

    res.render('pages/home', {
      newsData,
      username: user.username,
      balance: user.balance,
    });
  } catch (err) {
    console.error('Error in /home route:', err);
    res.render('pages/home', { newsData: {} });
  }
});


app.get('/login', (req, res) => {
  res.render('pages/login');
});

app.post('/login', async (req, res) => {
  let body = req.body;
  const query = `
  SELECT *
  FROM users
  WHERE username = $1`;
  try {
    let result = await db.oneOrNone(query, [body.username]);
    if (!result) {
      throw new Error();
    }
    const match = await bcrypt.compare(body.password, result.password_hash);
    if (!match) {
      throw new Error();
    }
    req.session.user = result.id;
    req.session.save();
    res.redirect('/home');
  } catch (err) {
    res.render('pages/login');
  }
});

app.get('/register', (req, res) => {
  res.render('pages/register');
});

app.post('/register', async (req, res) => {
  let body = req.body;
  const query = `
  INSERT INTO users
    (username, email, password_hash, balance)
  VALUES
    ($1, $2, $3, $4)`;
  try {
    if (!body.username || !body.password || !body.email) {
      throw new Error();
    }
    const password_hash = await bcrypt.hash(body.password, 10);
    await db.none(query, [body.username, body.email, password_hash, 1000]);
    res.redirect('/login');
  } catch (err) {
    res.redirect('/register');
  }
});

app.get('/logout', auth, (req, res) => {
  req.session.destroy(() => {
    res.redirect('/login');
  });
});

app.get('/profile', auth, async (req, res) => {
  const query = `
    SELECT *
    FROM users
    WHERE id = $1
    `;
  try {
    const result = await db.one(query, [req.session.user]);
    res.render('pages/profile', {
      username: result.username,
      email: result.email,
      balance: result.balance,
      is_active: result.is_active
    });
  } catch (err) {
    res.redirect('/home');
  }
});

app.post('/delete', auth, async (req, res) => {
  const query = `
    DELETE FROM users
    WHERE id = $1
  `;
  try {
    await db.none(query, [req.session.user]);
    res.redirect('/logout');
  } catch (err) {
    res.redirect('/home');
  }
});

let currentSort = 'DESC';

app.get('/leaderboard', auth, async (req, res) => {
  const query = `
    SELECT username, balance 
    FROM users
    WHERE is_active = TRUE
    ORDER BY balance ${currentSort}
    LIMIT 5
  `;
  try {
    const result = await db.any(query);
    res.render('pages/leaderboard', { topUsers: result, currentSort: currentSort});
  } catch(err) {
    res.redirect('/profile');
  }
});

app.get('/changeSort', async (req, res) => {
  currentSort = (currentSort == 'DESC') ? 'ASC' : 'DESC';
  res.redirect('/leaderboard');
});

app.get('/asset/:symbol', (req, res) => {
  const symbol = req.params.symbol;
  res.render('pages/asset', { symbol });
});

app.post('/trade', auth, async (req, res) => {
  const { symbol, quantity, action } = req.body;
  const userId = req.session.user;

  try {
    // Call Flask API which uses User.load_from_db() + user.buy()/sell() to update DB
    const response = await axios.post(`http://api:5000/${action}`, {
      user_id: userId,
      symbol: symbol,
      quantity: parseFloat(quantity)
    });

    res.redirect(`/asset/${symbol}`);
  } catch (err) {
    const errorMsg = err.response?.data?.error || 'Trade failed';
    console.error('Trade error:', errorMsg);
    res.redirect(`/asset/${symbol}`);
  }
});


// API endpoints for testing
app.get('/welcome', (req, res) => {
  res.json({ status: 'success', message: 'Welcome!' });
});

// API endpoint for tests - JSON register endpoint  
app.post('/api/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;

    // Validate input
    if (!username || !email || !password) {
      return res.status(400).json({ message: 'Invalid input' });
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ message: 'Invalid input' });
    }

    // Hash password
    const hashedPassword = await bcryptjs.hash(password, 10);

    // Insert user into database with retry logic
    let retries = 3;
    let lastError;

    while (retries > 0) {
      try {
        await db.none(
          'INSERT INTO users (username, email, password_hash, balance) VALUES ($1, $2, $3, $4)',
          [username, email, hashedPassword, 1000]
        );
        return res.status(200).json({ message: 'Success' });
      } catch (dbError) {
        lastError = dbError;
        retries--;
        if (retries > 0) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }
    }

    throw lastError;
  } catch (error) {
    // Handle duplicate username or email
    if (error.message && (error.message.includes('unique') || error.message.includes('duplicate'))) {
      return res.status(400).json({ message: 'Invalid input' });
    }
    console.error('Register error:', error);
    res.status(400).json({ message: 'Invalid input' });
  }
});

const cache = {};
const CACHE_DURATION = 60 * 15 * 1000; // 15 minutes

async function getOHLCForChart(symbol) {
  const now = Date.now();

  if (cache[symbol] && (now - cache[symbol].timestamp) < CACHE_DURATION) {
    console.log(`Using cached data for ${symbol}`);
    return cache[symbol].data;
  }

  const response = await fetch(`http://api:5000/twelvedata/${symbol}`);
  const data = await response.json();
  const values = data.data?.values;

  if (!values) {
    console.error(`Bad response for ${symbol}:`, data.data);
    return cache[symbol]?.data || [];
  }

  
  const ohlc = values
    .map(v => ({
      time: v.datetime,
      open: parseFloat(v.open),
      high: parseFloat(v.high),
      low:  parseFloat(v.low),
      close: parseFloat(v.close),
    }))
    .sort((a, b) => a.time.localeCompare(b.time));

  cache[symbol] = { data: ohlc, timestamp: now };
  return ohlc;
}

async function getIntradayForChart(symbol) {
  const cacheKey = `${symbol}_intraday`;
  const now = Date.now();

  if (cache[cacheKey] && (now - cache[cacheKey].timestamp) < CACHE_DURATION) {
    console.log(`Using cached intraday for ${symbol}`);
    return cache[cacheKey].data;
  }

  const response = await fetch(`http://api:5000/intraday/${symbol}`);
  const data = await response.json();
  const values = data.data?.values;

  if (!values) {
    console.error(`Bad intraday response for ${symbol}`);
    return cache[cacheKey]?.data || [];
  }

  const ohlc = values
    .map(v => ({
      time: Math.floor(new Date(v.datetime).getTime() / 1000), // convert to Unix timestamp
      open: parseFloat(v.open),
      high: parseFloat(v.high),
      low:  parseFloat(v.low),
      close: parseFloat(v.close),
    }))
    .sort((a, b) => a.time - b.time);

  cache[cacheKey] = { data: ohlc, timestamp: now };
  return ohlc;
}
  
const newsCache = {};
const NEWS_CACHE_DURATION = 2 * 60 * 60 * 1000; // 2 hours in ms

async function getCachedNews(symbol) {
  const now = Date.now();

  if (newsCache[symbol] && (now - newsCache[symbol].timestamp) < NEWS_CACHE_DURATION) {
    console.log(`Using cached news for ${symbol}`);
    return newsCache[symbol].data;
  }

  try {
    const response = await axios.get(`http://api:5000/news/${symbol}`);
    const data = response.data;
    newsCache[symbol] = { data, timestamp: now };
    return data;
  } catch (err) {
    console.error(`Error fetching news for ${symbol}:`, err.message);
    return { articles: [] };
  }
}

app.get("/feed", auth, async (req, res) => {
  const symbols = [
    { short: "AAPL", symbol: "AAPL", name: "Apple Inc." },
    { short: "TSLA", symbol: "TSLA", name: "Tesla Inc." },
    { short: "NVDA", symbol: "NVDA", name: "NVIDIA Corp." },
    { short: "AMZN", symbol: "AMZN", name: "Amazon.com Inc." },
    { short: "GOOGL", symbol: "GOOGL", name: "Alphabet Inc." },
    { short: "MSFT", symbol: "MSFT", name: "Microsoft Corp." },
    { short: "META", symbol: "META", name: "Meta Platforms Inc." },
    { short: "NFLX", symbol: "NFLX", name: "Netflix Inc." }
  ];

  const tickers = await Promise.all(symbols.map(async (t) => {
    const intradayData = await getIntradayForChart(t.symbol);
    return { ...t, intradayData };
  }));

  res.render('pages/feed', { tickers });
});

// *****************************************************
// <!-- Section 5 : Start Server-->
// *****************************************************

module.exports = app.listen(3000);
