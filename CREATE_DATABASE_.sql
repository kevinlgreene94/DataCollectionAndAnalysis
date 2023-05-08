DROP DATABASE IF EXISTS SWDV_DATABASE;

CREATE DATABASE SWDV_DATABASE;


USE SWDV_DATABASE;


CREATE TABLE `company_tech` (
  `ct_id` int PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `company_id` int NOT NULL,
  `ct_techid` int NOT NULL,
  `ct_usednow` ENUM('yes', 'no', 'unknown') NOT NULL DEFAULT 'unknown',
  `ct_shouldteach` ENUM('yes', 'no', 'unknown') NOT NULL DEFAULT 'unknown',
  `ct_topthree` ENUM('yes', 'no', 'unknown') DEFAULT 'unknown',
  `ct_continue` ENUM('yes', 'no', 'unknown') NOT NULL DEFAULT 'unknown',
  `tc_collectdate` DATE NOT NULL
);

CREATE TABLE `company` (
  `company_id` int PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `company_name` varchar(100) NOT NULL,
  `company_street` varchar(150),
  `company_state` enum("AL", "AK", "AZ", "AR", "CA", "CZ", "CO", "CT", "DE", "DC", "FL", "GA", "GU", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VI", "VA", "WA", "WV", "WI", "WY"),
  `company_zip` varchar(20),
  `company_size` int NOT NULL,
  `company_area` enum('technology', 'healthcare', 'manufacturing', 'banking', 'investments', 'marketing', 'architechture', 'education', 'government', 'grocery'),
  `company_hire2year` ENUM('yes', 'no', 'unknown') NOT NULL,
  `company_intern` ENUM('yes', 'no', 'unknown') NOT NULL
);

CREATE TABLE `contacts` (
  `contact_id` int PRIMARY KEY AUTO_INCREMENT,
  `company_id` int NOT NULL,
  `contact_last` varchar(50) NOT NULL,
  `contact_first` varchar(50) NOT NULL,
  `contact_area` enum('it','clevel','security', 'dev', 'other') NOT NULL,
  `contact_phone` varchar(20) NOT NULL,
  `contact_lastcomm` date NOT NULL DEFAULT CURRENT_DATE,
  `contact_future` ENUM('yes', 'no', 'unknown') NOT NULL,
  `contact_notes` TEXT 
);

CREATE TABLE `technologies` (
  `tech_id` int PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `tech_area` enum('frontend_lang', 'frontend_frame', 'backend_lang', 'backend_frame', 'mobile', 'network', 'security', 'devops', 'analytics', 'database', 'cloud', 'communication', 'other') NOT NULL,
  `tech_name` varchar(100) NOT NULL	
 );


ALTER TABLE `contacts` ADD FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`);

ALTER TABLE `company_tech` ADD FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`);

ALTER TABLE `company_tech` ADD FOREIGN KEY (`ct_techid`) REFERENCES `technologies` (`tech_id`);


DROP PROCEDURE IF EXISTS SWDV_DATABASE.EnterCompanies;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.EnterCompanies(IN name varchar(255), IN street varchar(150),
	IN state varchar(20), IN zip varchar(20), IN cmp_size int,
	IN area enum('technology', 'healthcare', 'manufacturing', 'banking', 'investments', 'marketing', 'architechture', 'education', 'government', 'grocery'), 
	IN hire2year ENUM('yes', 'no', 'unknown') , IN intern ENUM('yes', 'no', 'unknown') )
BEGIN
	INSERT INTO company(company_name, company_street, company_state, company_zip, company_size, company_area, company_hire2year, company_intern)
	VALUES (name, street, state, zip, cmp_size, area, hire2year, intern);
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS SWDV_DATABASE.EnterTechnologies;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.EnterTechnologies(IN name varchar(100), IN area enum('frontend_lang', 'frontend_frame', 'backend_lang', 'backend_frame', 'mobile', 'network', 'security', 'devops', 'analytics', 'database', 'cloud', 'communication'))
BEGIN
	INSERT INTO technologies(tech_area, tech_name)
	VALUES (area, name);
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS SWDV_DATABASE.EnterCompanyTech;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.EnterCompanyTech(IN companyID int, IN tech_id int, IN used_now ENUM('yes', 'no', 'unknown') , IN should_teach ENUM('yes', 'no', 'unknown') , IN topthree ENUM('yes', 'no', 'unknown') , IN ct_continue ENUM('yes', 'no', 'unknown'), IN collect_date date )
BEGIN
	INSERT INTO company_tech(company_id, ct_techid, ct_usednow, ct_shouldteach, ct_topthree, ct_continue, tc_collectdate) 
	VALUES (companyID, tech_id, used_now, should_teach, topthree, ct_continue, collect_date);
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS SWDV_DATABASE.EnterContact;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.EnterContact(IN companyID int, IN ct_last varchar(50), IN ct_first varchar(50), IN ct_area enum('it','clevel','security','dev','other') , IN ct_phone varchar(20), IN ct_lastcomm date, IN ct_future ENUM('yes', 'no', 'unknown') , IN ct_notes TEXT)
BEGIN
	INSERT INTO contacts(company_id, contact_last, contact_first, contact_area, contact_phone, contact_lastcomm, contact_future, contact_notes) 
	VALUES (companyID, ct_last, ct_first, ct_area, ct_phone, ct_lastcomm, ct_future, ct_notes);
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS SWDV_DATABASE.ModifyCompany;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.ModifyCompany(IN companyID int, IN name varchar(255), IN street varchar(150),
	IN state varchar(20), IN zip varchar(20), IN cmp_size int,
	IN area enum('technology', 'healthcare', 'manufacturing', 'banking', 'investments', 'marketing', 'architechture', 'education', 'government', 'grocery'), 
	IN hire2year ENUM('yes', 'no', 'unknown') , IN intern ENUM('yes', 'no', 'unknown') )
BEGIN
	UPDATE company
	SET company_name = name, company_street = street, company_state = state, company_zip = zip, company_size = cmp_size, company_area = area, company_hire2year = hire2year, company_intern = intern
	WHERE company_id = companyID;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS SWDV_DATABASE.ModifyCompanyTech;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.ModifyCompanyTech(IN ctID int, IN companyID int, IN tech_id int, IN used_now ENUM('yes', 'no', 'unknown') , IN should_teach ENUM('yes', 'no', 'unknown') , IN topthree ENUM('yes', 'no', 'unknown') , IN ctContinue ENUM('yes', 'no', 'unknown'), IN collect_date date )
BEGIN
	UPDATE company_tech
	SET company_id = companyID, ct_techid = tech_id, ct_usednow = used_now, ct_shouldteach = should_teach, ct_topthree = topthree, ct_continue = ctContinue,  tc_collectdate = collect_date
	WHERE ct_id = ctID;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS SWDV_DATABASE.ModifyContacts;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.ModifyContacts(IN ct_id int, IN companyID int, IN ct_last varchar(50), IN ct_first varchar(50), IN ct_area enum('it','clevel','security','dev','other') , IN ct_phone varchar(20), IN ct_lastcomm date, IN ct_future ENUM('yes', 'no', 'unknown') , IN ct_notes TEXT)
BEGIN
	UPDATE contacts
	SET company_id = companyID, contact_last = ct_last, contact_first = ct_first, contact_area = ct_area, contact_phone = ct_phone, contact_lastcomm = ct_lastcomm,  contact_future = ct_future, contact_notes = ct_notes
	WHERE contact_id = ct_id;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS SWDV_DATABASE.DeleteContact;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.DeleteContact(IN ctID int)
BEGIN
	DELETE FROM contacts WHERE contact_id = ctID;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS SWDV_DATABASE.DeleteCompanyTech;

DELIMITER $$
$$
CREATE PROCEDURE SWDV_DATABASE.DeleteCompanyTech(IN ctID int)
BEGIN
	DELETE FROM company_tech WHERE ct_id = ctID;
END$$
DELIMITER ;
