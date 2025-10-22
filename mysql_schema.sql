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
    password VARCHAR(255) NOT NULL,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create the nsf_personnel_compensation table
CREATE TABLE nsf_personnel_compensation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(100) NOT NULL,
    y2_rate_increase DECIMAL(5,2) NOT NULL,
    y3_rate_increase DECIMAL(5,2) NOT NULL,
    y4_rate_increase DECIMAL(5,2) NOT NULL,
    y5_rate_increase DECIMAL(5,2) NOT NULL
);
INSERT INTO nsf_personnel_compensation (role, y2_rate_increase, y3_rate_increase, y4_rate_increase, y5_rate_increase) VALUES
('PI', 0.20, 0.20, 0.20, 0.20),
('Co-PI', 0.15, 0.15, 0.15, 0.15),
('UI Professional Staff & Post Docs', 0.10, 0.10, 0.10, 0.10),
('GRAs/UGrads', 0.05, 0.05, 0.05, 0.05),
('Temp Help', 0.02, 0.02, 0.02, 0.02);

-- Create the nih_personnel_compensation table
CREATE TABLE nih_personnel_compensation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(100) NOT NULL,
    y2_rate_increase DECIMAL(5,2) NOT NULL,
    y3_rate_increase DECIMAL(5,2) NOT NULL,
    y4_rate_increase DECIMAL(5,2) NOT NULL,
    y5_rate_increase DECIMAL(5,2) NOT NULL
);
INSERT INTO nih_personnel_compensation (role, y2_rate_increase, y3_rate_increase, y4_rate_increase, y5_rate_increase) VALUES
('PI', 0.25, 0.20, 0.18, 0.15),
('Co-PI', 0.22, 0.18, 0.16, 0.14),
('Senior Researcher', 0.18, 0.15, 0.12, 0.10),
('Postdoctoral Fellow', 0.12, 0.10, 0.08, 0.06),
('GRAs/UGrads', 0.07, 0.06, 0.05, 0.05),
('Temp Help', 0.03, 0.03, 0.02, 0.02);



-- Table: expense_categories
CREATE TABLE IF NOT EXISTS expense_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

 -- Table: expense_subcategories
CREATE TABLE IF NOT EXISTS expense_subcategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
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
INSERT INTO fringe_rates (role, year, fringe_rate) VALUES
-- Faculty
('Faculty', 1, 31.00),
('Faculty', 2, 31.00),
('Faculty', 3, 31.00),
('Faculty', 4, 31.00),
('Faculty', 5, 31.00),

-- UI professional staff & Post Docs
('UI professional staff & Post Docs', 1, 41.30),
('UI professional staff & Post Docs', 2, 41.30),
('UI professional staff & Post Docs', 3, 41.30),
('UI professional staff & Post Docs', 4, 41.30),
('UI professional staff & Post Docs', 5, 41.30),

-- GRAs/UGrads
('GRAs/UGrads', 1, 2.50),
('GRAs/UGrads', 2, 2.50),
('GRAs/UGrads', 3, 2.50),
('GRAs/UGrads', 4, 2.50),
('GRAs/UGrads', 5, 2.50),

-- Temp Help
('Temp Help', 1, 8.30),
('Temp Help', 2, 8.30),
('Temp Help', 3, 8.30),
('Temp Help', 4, 8.30),
('Temp Help', 5, 8.30);





-- NSF Fringe Rates Table
CREATE TABLE nsf_fringe_rates (
  id INT NOT NULL AUTO_INCREMENT,
  role VARCHAR(50) NOT NULL,
  year INT NOT NULL CHECK (year BETWEEN 1 AND 6),
  fringe_rate DECIMAL(5,2) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO nsf_fringe_rates (role, year, fringe_rate) VALUES
-- Faculty
('Faculty', 1, 31.00),
('Faculty', 2, 31.00),
('Faculty', 3, 31.00),
('Faculty', 4, 31.00),
('Faculty', 5, 31.00),

-- UI professional staff & Post Docs
('UI professional staff & Post Docs', 1, 41.30),
('UI professional staff & Post Docs', 2, 41.30),
('UI professional staff & Post Docs', 3, 41.30),
('UI professional staff & Post Docs', 4, 41.30),
('UI professional staff & Post Docs', 5, 41.30),

-- GRAs/UGrads
('GRAs/UGrads', 1, 2.50),
('GRAs/UGrads', 2, 2.50),
('GRAs/UGrads', 3, 2.50),
('GRAs/UGrads', 4, 2.50),
('GRAs/UGrads', 5, 2.50),

-- Temp Help
('Temp Help', 1, 8.30),
('Temp Help', 2, 8.30),
('Temp Help', 3, 8.30),
('Temp Help', 4, 8.30),
('Temp Help', 5, 8.30);


-- NIH Fringe Rates Table
CREATE TABLE nih_fringe_rates (
  id INT NOT NULL AUTO_INCREMENT,
  role VARCHAR(50) NOT NULL,
  year INT NOT NULL CHECK (year BETWEEN 1 AND 6),
  fringe_rate DECIMAL(5,2) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO nih_fringe_rates (role, year, fringe_rate) VALUES
-- Faculty
('Faculty', 1, 32.00),
('Faculty', 2, 32.00),
('Faculty', 3, 32.00),
('Faculty', 4, 32.00),
('Faculty', 5, 32.00),

-- UI professional staff & Post Docs
('UI professional staff & Post Docs', 1, 39.50),
('UI professional staff & Post Docs', 2, 39.50),
('UI professional staff & Post Docs', 3, 39.50),
('UI professional staff & Post Docs', 4, 39.50),
('UI professional staff & Post Docs', 5, 39.50),

-- GRAs/UGrads
('GRAs/UGrads', 1, 3.00),
('GRAs/UGrads', 2, 3.00),
('GRAs/UGrads', 3, 3.00),
('GRAs/UGrads', 4, 3.00),
('GRAs/UGrads', 5, 3.00),

-- Temp Help
('Temp Help', 1, 9.00),
('Temp Help', 2, 9.00),
('Temp Help', 3, 9.00),
('Temp Help', 4, 9.00),
('Temp Help', 5, 9.00);






-- Create the grants table
CREATE TABLE IF NOT EXISTS grants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    description TEXT, 
    funding_agency VARCHAR(255) NOT NULL, 
    duration = db.Column(Integer, nullable=False) 
    start_date DATE NOT NULL, 
    end_date DATE NOT NULL,  
    status ENUM('Draft', 'Submitted', 'Approved', 'Rejected', 'Completed') DEFAULT 'Draft',  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);




-- Recreate grants_personnel table with NULLs allowed and default values
CREATE TABLE grants_personnel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grant_id INT NOT NULL,
    name VARCHAR(100) DEFAULT NULL,
    position VARCHAR(100) DEFAULT NULL,
    year INT DEFAULT NULL,
    estimated_hours DECIMAL(10, 2) DEFAULT NULL,
    FOREIGN KEY (grant_id) REFERENCES grants(id) ON DELETE CASCADE
);



-- Grants Travel table
CREATE TABLE grants_travel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grant_id INT NOT NULL,
    travel_type ENUM('Domestic', 'International') DEFAULT NULL,
    name VARCHAR(255) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    year INT DEFAULT NULL,
    amount DECIMAL(10, 2) DEFAULT NULL,
    FOREIGN KEY (grant_id) REFERENCES grants(id) ON DELETE CASCADE
);

-- Recreate grants_materials table with NULLs allowed and default values
CREATE TABLE grants_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grant_id INT NOT NULL,
    category_id INT DEFAULT NULL,
    subcategory_id INT DEFAULT NULL,
    cost DECIMAL(10, 2) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    year INT DEFAULT NULL,
    
    FOREIGN KEY (grant_id) REFERENCES grants(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES expense_categories(id),
    FOREIGN KEY (subcategory_id) REFERENCES expense_subcategories(id)
);

-- tables for each personeels
-- PI Table
CREATE TABLE pi_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    position VARCHAR(100) NOT NULL,
    expected_hourly_salary DECIMAL(10,2) NOT NULL
);

-- Co-PI Table
CREATE TABLE copi_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    position VARCHAR(100) NOT NULL,
    expected_hourly_salary DECIMAL(10,2) NOT NULL
);

-- Professional Staff Table
CREATE TABLE professionalstaff_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    position VARCHAR(100) NOT NULL,
    expected_hourly_salary DECIMAL(10,2) NOT NULL
);

-- Postdoc Table
CREATE TABLE postdoc_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    position VARCHAR(100) NOT NULL,
    expected_hourly_salary DECIMAL(10,2) NOT NULL
);

-- GRA Table
CREATE TABLE gra_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    position VARCHAR(100) NOT NULL,
    expected_hourly_salary DECIMAL(10,2) NOT NULL
);

-- Temp Help Table
CREATE TABLE temphelp_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    position VARCHAR(100) NOT NULL,
    expected_hourly_salary DECIMAL(10,2) NOT NULL
);

-- Undergrad Table
CREATE TABLE undergrad_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    position VARCHAR(100) NOT NULL,
    expected_hourly_salary DECIMAL(10,2) NOT NULL
);


-- PI Table
INSERT INTO pi_table (full_name, email, position, expected_hourly_salary) VALUES
('Dr. Alice Morgan', 'alice.morgan@university.edu', 'PI', 57.69),
('Dr. Brian Hill', 'brian.hill@university.edu', 'PI', 55.29),
('Dr. Carol White', 'carol.white@institute.edu', 'PI', 60.10),
('Dr. David Chen', 'david.chen@researchlab.org', 'PI', 52.88),
('Dr. Emily Ray', 'emily.ray@university.edu', 'PI', 56.73),
('Dr. Frank Harris', 'frank.harris@college.edu', 'PI', 58.65),
('Dr. Grace Liu', 'grace.liu@medcenter.org', 'PI', 57.21),
('Dr. Henry West', 'henry.west@sciencehub.org', 'PI', 58.41);

-- Co-PI Table
INSERT INTO copi_table (full_name, email, position, expected_hourly_salary) VALUES
('Dr. Irene Brooks', 'irene.brooks@university.edu', 'Co-PI', 45.67),
('Dr. James Carter', 'james.carter@institute.edu', 'Co-PI', 47.12),
('Dr. Karen Singh', 'karen.singh@researchlab.org', 'Co-PI', 45.19),
('Dr. Liam Zhang', 'liam.zhang@college.edu', 'Co-PI', 44.23),
('Dr. Monica Diaz', 'monica.diaz@medcenter.org', 'Co-PI', 46.63),
('Dr. Nathan Ford', 'nathan.ford@university.edu', 'Co-PI', 44.71),
('Dr. Olivia Dean', 'olivia.dean@sciencehub.org', 'Co-PI', 46.15);

-- Professional Staff Table
INSERT INTO professionalstaff_table (full_name, email, position, expected_hourly_salary) VALUES
('Alice Stevens', 'alice.stevens@institute.edu', 'Professional Staff', 36.06),
('Brandon Mills', 'brandon.mills@university.edu', 'Professional Staff', 35.10),
('Catherine Lin', 'catherine.lin@research.org', 'Professional Staff', 34.62),
('Daniel Kim', 'daniel.kim@medcenter.org', 'Professional Staff', 35.58),
('Ella Graham', 'ella.graham@sciencehub.org', 'Professional Staff', 36.54),
('Felix Torres', 'felix.torres@university.edu', 'Professional Staff', 34.86),
('Grace Park', 'grace.park@college.edu', 'Professional Staff', 36.30);

-- Postdoc Table
INSERT INTO postdoc_table (full_name, email, position, expected_hourly_salary) VALUES
('Isaac Moore', 'isaac.moore@university.edu', 'Postdoc', 28.85),
('Julia Smith', 'julia.smith@institute.edu', 'Postdoc', 29.81),
('Kevin Patel', 'kevin.patel@researchlab.org', 'Postdoc', 28.37),
('Laura Johnson', 'laura.johnson@college.edu', 'Postdoc', 29.33),
('Mark Robinson', 'mark.robinson@medcenter.org', 'Postdoc', 29.09),
('Nina Ali', 'nina.ali@sciencehub.org', 'Postdoc', 30.29),
('Oscar Wu', 'oscar.wu@university.edu', 'Postdoc', 29.57);

-- GRA Table
INSERT INTO gra_table (full_name, email, position, expected_hourly_salary) VALUES
('Abigail White', 'abigail.white@university.edu', 'GRA', 13.46),
('Benjamin Lee', 'benjamin.lee@institute.edu', 'GRA', 12.98),
('Chloe Evans', 'chloe.evans@researchlab.org', 'GRA', 12.50),
('Dylan Scott', 'dylan.scott@college.edu', 'GRA', 13.22),
('Emma Wright', 'emma.wright@university.edu', 'GRA', 13.70),
('Finn Taylor', 'finn.taylor@medcenter.org', 'GRA', 12.74),
('Gabriella Ross', 'gabriella.ross@sciencehub.org', 'GRA', 13.94);

-- Temp Help Table
INSERT INTO temphelp_table (full_name, email, position, expected_hourly_salary) VALUES
('Henry Adams', 'henry.adams@university.edu', 'Temp Help', 9.62),
('Isla Moore', 'isla.moore@institute.edu', 'Temp Help', 10.10),
('Jack Bennett', 'jack.bennett@researchlab.org', 'Temp Help', 9.38),
('Kylie Nelson', 'kylie.nelson@college.edu', 'Temp Help', 9.86),
('Leo Turner', 'leo.turner@medcenter.org', 'Temp Help', 9.52),
('Mia Cooper', 'mia.cooper@sciencehub.org', 'Temp Help', 9.71),
('Noah Harris', 'noah.harris@university.edu', 'Temp Help', 9.95);

-- Undergrad Table
INSERT INTO undergrad_table (full_name, email, position, expected_hourly_salary) VALUES
('Anna Green', 'anna.green@university.edu', 'Undergrad', 7.21),
('Brandon Lee', 'brandon.lee@college.edu', 'Undergrad', 6.97),
('Clara Patel', 'clara.patel@institute.edu', 'Undergrad', 7.12),
('Daniel Reyes', 'daniel.reyes@researchlab.org', 'Undergrad', 7.31),
('Emily Foster', 'emily.foster@university.edu', 'Undergrad', 7.16),
('Frankie Simmons', 'frankie.simmons@college.edu', 'Undergrad', 7.26),
('Gina Cho', 'gina.cho@medcenter.org', 'Undergrad', 7.07),
('Henry Blake', 'henry.blake@sciencehub.org', 'Undergrad', 7.36);





/* travel itenary */
-- one row per “travel” (domestic or international) in a separate itinerary table
CREATE TABLE IF NOT EXISTS travel_itineraries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  travel_id INT NOT NULL, 
  departure_date DATE      NULL,
  arrival_date   DATE      NULL,
  flight_cost    DECIMAL(10,2) NULL,
  days_stay            INT       NULL,
  per_day_food_lodging DECIMAL(10,2) NULL,
  per_day_transportation DECIMAL(10,2) NULL,
  
  UNIQUE KEY uq_travel (travel_id),

  FOREIGN KEY (travel_id)
    REFERENCES grants_travel(id)
    ON DELETE CASCADE
);





CREATE TABLE graduate_student_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_type VARCHAR(50) NOT NULL DEFAULT 'PhD',
    base_tuition_per_semester DECIMAL(10,2) NOT NULL, 
    summer_credit_cost DECIMAL(10,2) NOT NULL,        
    health_insurance_cost DECIMAL(10,2) NOT NULL,     
    num_semesters_per_year INT NOT NULL DEFAULT 2,
    annual_increase_percent DECIMAL(5,2) NOT NULL DEFAULT 3.00,
    total_years INT NOT NULL DEFAULT 3
);
INSERT INTO graduate_student_costs (
    base_tuition_per_semester,
    summer_credit_cost,
    health_insurance_cost
) VALUES (
    5408.00,  
    601.00,   
    1100.00    
);
