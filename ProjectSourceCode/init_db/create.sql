--CREATING TABLE USER_INFO attriubutes may need to be changed to match other create sql
CREATE TABLE IF NOT EXISTS USER_INFO(
    User_ID SERIAL PRIMARY KEY,
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
--CREATING TABLE USER_BALANCE attriubutes may need to be changed to match other create sql
CREATE TABLE IF NOT EXISTS USER_BALANCE(
    User_ID INT PRIMARY KEY,
    Balance DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (User_ID) REFERENCES USER_INFO(User_ID)
);


