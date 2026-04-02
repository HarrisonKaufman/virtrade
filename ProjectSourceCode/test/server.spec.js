// ********************** Initialize server **********************************

const app = require('../index.js'); //TODO: Make sure the path to your index.js is correctly added

// ********************** Import Libraries ***********************************

const chai = require('chai'); // Chai HTTP provides an interface for live integration testing of the API's.
const chaiHttp = require('chai-http');
chai.should();
chai.use(chaiHttp);
const {assert, expect} = chai;

// ********************** DEFAULT WELCOME TESTCASE ****************************

describe('Server!', () => {
  // Sample test case given to test / endpoint.
  it('Returns the default welcome message', done => {
    chai
      .request(app)
      .get('/welcome')
      .end((err, res) => {
        expect(res).to.have.status(200);
        expect(res.body.status).to.equals('success');
        assert.strictEqual(res.body.message, 'Welcome!');
        done();
      });
  });
});

// *********************** TODO: WRITE 2 UNIT TESTCASES **************************

describe('Testing Register API', () => {
  // Positive Test Case
  it('positive : /register - should register a new user with valid credentials', done => {
    chai
      .request(app)
      .post('/register')
      .send({
        username: 'testuser123',
        email: 'testuser@example.com',
        password: 'SecurePass123!'
      })
      .end((err, res) => {
        expect(res).to.have.status(200);
        expect(res.body).to.have.property('message');
        expect(res.body.message).to.equal('Success');
        done();
      });
  });

  // Negative Test Case
  it('negative : /register - should reject registration with invalid email', done => {
    chai
      .request(app)
      .post('/register')
      .send({
        username: 'anotheruser',
        email: 'invalid-email-format',
        password: 'SecurePass123!'
      })
      .end((err, res) => {
        expect(res).to.have.status(400);
        expect(res.body).to.have.property('message');
        expect(res.body.message).to.equal('Invalid input');
        done();
      });
  });
});

// ********************************************************************************