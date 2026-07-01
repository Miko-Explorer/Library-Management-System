#Create database for our system:
CREATE DATABASE library_db; 

#Set as default schema:
USE library_db; 

#Books entity - book information:
CREATE TABLE books(
	book_id INT AUTO_INCREMENT PRIMARY KEY, 
  book_title VARCHAR(500) NOT NULL UNIQUE, 
  book_genre ENUM('Action Adventure', 'Classics', 
  'Fantasy', 'Graphic Novels', 'Historical Fiction', 
  'Horror', 'Mystery', 'Romance', 'Sci-Fi',
  'Suspense/Thriller') NOT NULL, 
  year_published YEAR NOT NULL
); 

#Member entity - member information:
CREATE TABLE members(
	member_id INT AUTO_INCREMENT PRIMARY KEY, 
  full_name VARCHAR(100) NOT NULL UNIQUE, 
  email VARCHAR(100) NOT NULL UNIQUE, 
  phone VARCHAR(11) NOT NULL UNIQUE,
  address CHAR(100) NOT NULL UNIQUE, 
  membership_date DATETIME NOT NULL, 
  is_active ENUM('Active', 'Inactive') NOT NULL 
)AUTO_INCREMENT = 100; 

#Loans entity - return and borrow of books information/status:
CREATE TABLE loans(
 loan_id INT AUTO_INCREMENT PRIMARY KEY, 
 book_id INT NOT NULL, 
 FOREIGN KEY(book_id) REFERENCES books(book_id), 
 member_id INT NOT NULL, 
 FOREIGN KEY(member_id) REFERENCES members(member_id), 
 loan_date DATETIME NOT NULL, 
 due_date DATETIME NOT NULL, 
 return_date DATETIME NOT NULL
)AUTO_INCREMENT = 200; 

#Fines entity - fines are applied if book's borrowed by members are not returned according to due to date:
CREATE TABLE fines(
	fine_id INT AUTO_INCREMENT PRIMARY KEY, 
  book_id INT NOT NULL, 
  FOREIGN KEY(book_id) REFERENCES books(book_id), 
  member_id INT NOT NULL, 
  FOREIGN KEY(member_id) REFERENCES members(member_id), 
  amount DECIMAL(5,2) DEFAULT 0.00, 
  reason ENUM('Lost', 'Damaged', 'Overdue') NOT NULL, 
  issued_date DATETIME NOT NULL, 
  paid DECIMAL(5,2) DEFAULT 0.00, 
  paid_date DATETIME NOT NULL
)AUTO_INCREMENT = 300; 

#Staff entity - staff information:
CREATE TABLE staff(
	staff_id INT AUTO_INCREMENT PRIMARY KEY, 
  full_name VARCHAR(100) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
	email VARCHAR(100) NOT NULL UNIQUE, 
  phone VARCHAR(11) NOT NULL UNIQUE,
  address CHAR(100) NOT NULL UNIQUE, 
  roles ENUM('Admin', 'Librarian', 'Asst. Librarian'),
  hire_date DATE NOT NULL, 
  last_login DATETIME NOT NULL,
  is_active ENUM('Active', 'Inactive') NOT NULL
);