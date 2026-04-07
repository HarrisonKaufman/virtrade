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

// test your database
db.connect()
  .then(obj => {
    console.log('Database connection successful'); // you can view this message in the docker compose logs
    obj.done(); // success, release the connection;
  })
  .catch(error => {
    console.log('ERROR:', error.message || error);
  });

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
// <!-- Section 4 : API Routes -->
// *****************************************************

app.get('/', (req, res) => {
    res.render('pages/login');
});

const auth = (req, res, next) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  next();
};

app.get('/home', auth, (req, res) => {
    res.render('pages/home');
});

app.get('/login', (req, res) => {
  res.render('pages/login');
});

app.get('/feed', (req, res) => {
  res.render('pages/feed');
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
  res.render('asset', { symbol });
});

app.post("/trade", (req, res) => {
  const { symbol, quantity, action } = req.body;
  // add user object/db logic here
  res.redirect(`/asset/${symbol}`);
});

// *****************************************************
// <!-- Section 5 : Start Server-->
// *****************************************************
// starting the server and keeping the connection open to listen for more requests
app.listen(3000);
console.log('Server is listening on port 3000');
