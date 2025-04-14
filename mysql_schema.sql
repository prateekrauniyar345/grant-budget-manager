-- Create the database
CREATE DATABASE IF NOT EXISTS grant_management;

-- Use the database
USE grant_management;

-- Create the users table with first_name and last_name
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- Store hashed password
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create the nsf_personnel_compensation table
CREATE TABLE nsf_personnel_compensation (
    id SERIAL PRIMARY KEY,
    role VARCHAR(100) NOT NULL, -- PI, Co-PI, GRAs, etc.
    base_hourly_rate DECIMAL(10,2) NOT NULL, 
    y2_rate_increase DECIMAL(5,2) NOT NULL, 
    y3_rate_increase DECIMAL(5,2) NOT NULL,
    y4_rate_increase DECIMAL(5,2) NOT NULL,
    y5_rate_increase DECIMAL(5,2) NOT NULL,
    y1_rate DECIMAL(10,2) GENERATED ALWAYS AS (base_hourly_rate) STORED,
    y2_rate DECIMAL(10,2) GENERATED ALWAYS AS (base_hourly_rate * (1 + y2_rate_increase)) STORED,
    y3_rate DECIMAL(10,2) GENERATED ALWAYS AS (y2_rate * (1 + y3_rate_increase)) STORED,
    y4_rate DECIMAL(10,2) GENERATED ALWAYS AS (y3_rate * (1 + y4_rate_increase)) STORED,
    y5_rate DECIMAL(10,2) GENERATED ALWAYS AS (y4_rate * (1 + y5_rate_increase)) STORED,
);

-- insert into NSF personnel_compensation table
INSERT INTO nsf_personnel_compensation (role, base_hourly_rate, y2_rate_increase, y3_rate_increase, y4_rate_increase, y5_rate_increase) 
VALUES
    ('PI', 50.00, 0.20, 0.20, 0.20, 0.20),
    ('Co-PI', 45.00, 0.15, 0.15, 0.15, 0.15),
    ('UI Professional Staff & Post Docs', 35.00, 0.10, 0.10, 0.10, 0.10),
    ('GRAs/UGrads', 25.00, 0.05, 0.05, 0.05, 0.05),
    ('Temp Help', 20.00, 0.02, 0.02, 0.02, 0.02);



-- create the nih_personnel_compensation table
CREATE TABLE nih_personnel_compensation (
    id SERIAL PRIMARY KEY,
    role VARCHAR(100) NOT NULL, -- PI, Co-PI, Post Docs, etc.
    base_hourly_rate DECIMAL(10,2) NOT NULL, 
    y2_rate_increase DECIMAL(5,2) NOT NULL, 
    y3_rate_increase DECIMAL(5,2) NOT NULL,
    y4_rate_increase DECIMAL(5,2) NOT NULL,
    y5_rate_increase DECIMAL(5,2) NOT NULL,
    y1_rate DECIMAL(10,2) GENERATED ALWAYS AS (base_hourly_rate) STORED,
    y2_rate DECIMAL(10,2) GENERATED ALWAYS AS (base_hourly_rate * (1 + y2_rate_increase)) STORED,
    y3_rate DECIMAL(10,2) GENERATED ALWAYS AS (y2_rate * (1 + y3_rate_increase)) STORED,
    y4_rate DECIMAL(10,2) GENERATED ALWAYS AS (y3_rate * (1 + y4_rate_increase)) STORED,
    y5_rate DECIMAL(10,2) GENERATED ALWAYS AS (y4_rate * (1 + y5_rate_increase)) STORED);

INSERT INTO nih_personnel_compensation (role, base_hourly_rate, y2_rate_increase, y3_rate_increase, y4_rate_increase, y5_rate_increase) 
VALUES
    ('PI', 60.00, 0.25, 0.20, 0.18, 0.15),
    ('Co-PI', 55.00, 0.22, 0.18, 0.16, 0.14),
    ('Senior Researcher', 45.00, 0.18, 0.15, 0.12, 0.10),
    ('Postdoctoral Fellow', 38.00, 0.12, 0.10, 0.08, 0.06),
    ('GRAs/UGrads', 28.00, 0.07, 0.06, 0.05, 0.05),
    ('Temp Help', 22.00, 0.03, 0.03, 0.02, 0.02);



-- Table: expense_categories
CREATE TABLE IF NOT EXISTS expense_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- Category name (e.g., "Equipment", "Travel")
    description TEXT, -- Optional description of the category
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

 -- Table: expense_subcategories
CREATE TABLE IF NOT EXISTS expense_subcategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL, -- Foreign key linking to expense_categories
    name VARCHAR(100) NOT NULL, -- Subcategory name (e.g., "Domestic", "International")
    description TEXT, -- Optional description of the subcategory
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES expense_categories(id)
);


-- Insert categories
INSERT INTO expense_categories (name, description)
VALUES 
    ('Equipment more than 5k', 'Items needed for the research project (e.g., tools, devices, machinery)'),
    ('Travel', 'Expenses related to domestic and international travel'),
    ('Participant support costs', 'Costs related to participant support (NSF only)'),
    ('Other direct costs', 'Other direct costs associated with the project');




-- Insert values for expense subcategories
INSERT INTO expense_subcategories (category_id, name, description) 
VALUES
    (1, 'Equipment >5K', 'Items needed for the research project (e.g., tools, devices, machinery) costing more than $5,000'),
    (2, 'Domestic Travel', 'Expenses related to domestic travel within the country'),
    (2, 'International Travel', 'Expenses related to international travel outside the country'),
    (3, 'Participant Support Costs (NSF)', 'Costs related to participant support (NSF only)'),
    (4, 'Materials and Supplies', 'Costs related to materials and supplies for the project'),
    (4, 'Equipment <5K', 'Small equipment or tools costing less than $5,000'),
    (4, 'Publication Costs', 'Costs related to publication and dissemination of results'),
    (4, 'Computer Services', 'Costs related to computer services needed for the project'),
    (4, 'Software', 'Costs related to software required for the project'),
    (4, 'Facility Usage Fees', 'Fees for using facilities required for the project'),
    (4, 'Conference Registration', 'Fees for conference registration and related costs'),
    (4, 'Other', 'Other expenses'),
    (4, 'Grad Student Tuition & Health Insurance', 'Graduate student tuition and health insurance costs');




-- Create the fringe_rates table
CREATE TABLE `fringe_rates` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `role` VARCHAR(50) NOT NULL,
  `year` INT NOT NULL CHECK (`year` BETWEEN 1 AND 6),
  `fringe_rate` DECIMAL(5,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insert data into the fringe_rates table
INSERT INTO `fringe_rates` (`role`, `year`, `fringe_rate`) VALUES
('Faculty', 1, 30.00),
('Faculty', 2, 30.50),
('Faculty', 3, 31.00),
('Faculty', 4, 31.50),
('Faculty', 5, 32.00),
('UI professional staff & Post Docs', 1, 32.00),
('UI professional staff & Post Docs', 2, 32.50),
('UI professional staff & Post Docs', 3, 33.00),
('UI professional staff & Post Docs', 4, 33.50),
('UI professional staff & Post Docs', 5, 34.00),
('GRAs/UGrads', 1, 20.00),
('GRAs/UGrads', 2, 20.50),
('GRAs/UGrads', 3, 21.00),
('GRAs/UGrads', 4, 21.50),
('GRAs/UGrads', 5, 22.00),
('Temp Help', 1, 10.00),
('Temp Help', 2, 10.50),
('Temp Help', 3, 11.00),
('Temp Help', 4, 11.50),
('Temp Help', 5, 12.00);





-- Create the grants table
CREATE TABLE IF NOT EXISTS grants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- Foreign key linking to users table
    title VARCHAR(255) NOT NULL,  -- Grant title
    description TEXT,  -- Detailed description of the grant
    funding_agency VARCHAR(255) NOT NULL,  -- Name of the funding agency (e.g., NSF, NIH)
    total_funding DECIMAL(15,2) NOT NULL,  -- Total funding amount
    start_date DATE NOT NULL,  -- Start date of the grant
    end_date DATE NOT NULL,  -- End date of the grant
    status ENUM('Draft', 'Submitted', 'Approved', 'Rejected', 'Completed') DEFAULT 'Draft',  -- Grant status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
