-- DDL: Data Definition Language

CREATE TABLE demo_tickets (
	id SERIAL PRIMARY KEY,
	title TEXT NOT NULL,
	priority TEXT NOT NULL
);

CREATE TABLE demo_comments (
	id SERIAL PRIMARY KEY,
	body TEXT NOT NULL,
	ticket_id INTEGER NOT NULL REFERENCES demo_tickets(id)		-- REFERENCES creates a foreign key 
);

/* other ddl:
	ALTER TABLE			- use to modify columns within an existing table
	DROP TABLE			- delete a table and all of its records
	TRUNCATE TABLE		- deltes all the records from a table, but keeps the table itself
*/

DROP TABLE demo_comments;
DROP TABLE demo_tickets;

TRUNCATE TABLE demo_comments;


-- DML: Data Manipulation Language

-- can insert without specifying properties but you have to give a value for EVERY column
-- INSERT INTO demo_tickets VALUES 
-- 	(1, 'Printer stopped working', 'low')
INSERT INTO demo_tickets (title, priority) VALUES 
	('Printer stopped working', 'low'),
	('Sales Report is unavailable', 'medium'),
	('Login SSO is failing', 'urgent'),
	('Printer stopped working', 'low'),
	('Sales Report is unavailable', 'medium'),
	('Login SSO is failing', 'urgent'),
	('Printer stopped working', 'low'),
	('Sales Report is unavailable', 'medium'),
	('Login SSO is failing', 'urgent');

INSERT INTO demo_comments (ticket_id, body) VALUES
	(1, 'tried printer in person. still failed after software update'),
	(1, 'ordering new printer'),
	(2, 'opening up sharepoint permissions');


SELECT * FROM demo_tickets;
SELECT * FROM demo_comments;

-- can specify only to get back certain fields
-- can do filtering with 'WHERE'
-- can give properties aliases with 'as'
SELECT title as Ticket_Title FROM demo_tickets WHERE priority = 'urgent';

-- organize outputs with 'ORDER BY'
-- restrict number of results with 'LIMIT' - returns first X number of records from the query
SELECT * FROM demo_tickets ORDER BY priority LIMIT 3;


/*
	JOINS
		combine results from multiple related tables
		'JOIN' defaults to INNER JOIN
		
		'INNER JOIN'				- only records that have an association between both tables
		'LEFT JOIN'/'RIGHT JOIN' 	- everything from one table and only matching records from the other
		'FULL JOIN'					- everything from both tables with nulls for all columns without values
*/
SELECT demo_tickets.title, demo_comments.body
FROM demo_tickets
JOIN demo_comments ON demo_comments.ticket_id = demo_tickets.id;

SELECT demo_tickets.title, demo_comments.body
FROM demo_tickets
LEFT JOIN demo_comments ON demo_comments.ticket_id = demo_tickets.id;

-- common to use aliases for your table names
SELECT t.title, c.body
FROM demo_tickets as t
LEFT JOIN demo_comments as c ON c.ticket_id = t.id;

-- update and delete existing records, MNAKE SURE TO INCLUDE A WHERE CLAUSE
UPDATE demo_tickets SET priority = 'high' WHERE id = 2;
DELETE FROM demo_tickets WHERE id = 3;

UPDATE demo_tickets SET priority = 'high';

-- cannot delete if a record is being referenced by another table's record
DELETE FROM demo_tickets;














