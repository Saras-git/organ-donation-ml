CREATE DATABASE organdonation;
USE organdonation;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(100),
    role VARCHAR(20),
    contact VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    hospital_name VARCHAR(100)
);

CREATE TABLE donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    blood_group VARCHAR(10),
    organ_donated VARCHAR(50),
    health_condition TEXT,
    contact_no VARCHAR(20),
    aadhar_no VARCHAR(20),
    address TEXT,
    hospital VARCHAR(100),
    entry_date DATETIME
);

CREATE TABLE recipients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    blood_group VARCHAR(10),
    organ_needed VARCHAR(50),
    urgency_level INT,
    contact_no VARCHAR(20),
    aadhar_no VARCHAR(20),
    address TEXT,
    hospital VARCHAR(100),
    entry_date DATETIME
);
SELECT * FROM users;
select * from donors;
select * from recipients;

