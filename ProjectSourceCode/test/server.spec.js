// ********************** Initialize server **********************************

const server = require('../index'); //TODO: Make sure the path to your index.js is correctly added

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
      .request(server)
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
  // Use a unique username with timestamp to avoid duplicates
  const timestamp = Date.now();
  const uniqueUsername = `testuser${timestamp}`;

  // Positive Test Case
  it('positive : /register - should register a new user with valid credentials', done => {
    chai
      .request(server)
      .post('/api/register')
      .send({
        username: uniqueUsername,
        email: `test${timestamp}@example.com`,
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
      .request(server)
      .post('/api/register')
      .send({
        username: `anotheruser${timestamp}`,
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