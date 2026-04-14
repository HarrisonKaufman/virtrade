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
    json: (context) => JSON.stringify(context)
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
        const symbols = ['AAPL', 'GOOGL', 'MSFT'];
        const newsData = {};
        
        for (const symbol of symbols) {
            const data = await getCachedNews(symbol);
            newsData[symbol] = data.articles || [];
        }
        
        res.render('pages/home', { newsData });
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
    if(!result) {
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
    if(!body.username || !body.password || !body.email) {
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
  } catch(err) {
    res.redirect('/home');
  }
});

app.post('/delete', auth, async (req, res) => {
  const query = `
    DELETE FROM USERS
    WHERE id = $1
  `;
  try {
    await db.none(query, [req.session.user]);
    res.redirect('/logout');
  } catch(err) {
    res.redirect('/home');
  }
});

app.get('/asset/:symbol', (req, res) => {
  const symbol = req.params.symbol;
  res.render('pages/asset', { symbol });
});

app.post('/trade', (req, res) => {
  const { symbol, quantity, action } = req.body;
  // add user object/db logic here
  res.redirect(`/asset/${symbol}`);
});

// API endpoints for testing
app.get('/welcome', (req, res) => {
  res.json({status: 'success', message: 'Welcome!'});
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
const CACHE_DURATION = 60 * 60 * 1000; // 1 hour in ms

async function getOHLCForChart(symbol) {
  const now = Date.now();

  if (cache[symbol] && (now - cache[symbol].timestamp) < CACHE_DURATION) {
    console.log(`Using cached data for ${symbol}`);
    return cache[symbol].data;
  }

  const response = await fetch(`http://api:5000/daily/${symbol}`);
  const data = await response.json();
  const timeSeries = data.data['Time Series (Daily)'];

  if (!timeSeries) {
    console.error(`Rate limited or bad response for ${symbol}`);
    return cache[symbol]?.data || [];
  }

  const ohlc = Object.entries(timeSeries)
    .map(([date, values]) => ({
      time: date,
      open: parseFloat(values['1. open']),
      high: parseFloat(values['2. high']),
      low:  parseFloat(values['3. low']),
      close: parseFloat(values['4. close']),
    }))
    .sort((a, b) => a.time.localeCompare(b.time));

  cache[symbol] = { data: ohlc, timestamp: now };
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
  ];

  const tickers = [];
  for (const t of symbols) {
    await new Promise(resolve => setTimeout(resolve, 1200));
    const ohlcData = await getOHLCForChart(t.symbol);
    tickers.push({ ...t, ohlcData });
  }

  res.render('pages/feed', { tickers });
});

// *****************************************************
// <!-- Section 5 : Start Server-->
// *****************************************************

module.exports = app.listen(3000);
