CREATE TABLE demo_customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE demo_orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES demo_customers(id),
    item TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL
);

INSERT INTO demo_customers (name) VALUES
    ('Ada Reyes'),
    ('Marcus Chen'),
    ('Priya Nair'),
    ('Devon Brooks'),
    ('Sofia Alvarez');

INSERT INTO demo_orders (customer_id, item, amount) VALUES
    (1, 'Desk Lamp', 34.99),
    (1, 'Office Chair', 129.00),
    (2, 'Monitor', 249.50),
    (3, 'Keyboard', 89.99),
    (3, 'Mouse', 24.99),
    (3, 'Webcam', 59.00),
    (5, 'Standing Desk', 399.00);

-- finds all orders and the customers that placed them
SELECT c.name, o.item
FROM demo_customers as c
JOIN demo_orders as o ON o.customer_id = c.id

-- find all customers that have placed an order
-- DISTINCT removes duplicates from results
SELECT DISTINCT c.name
FROM demo_customers c
JOIN demo_orders o ON c.id = o.customer_id;

-- find all customers who have NOT placed an order
-- Anti-Join pattern: doing a join to find where records are actually NOT related
SELECT c.name
FROM demo_customers c
LEFT JOIN demo_orders o ON c.id = o.customer_id
WHERE o.id IS NULL;


/*
	AGGREGATE FUNCTIONS
		group data together and summarize that grouping based on some value

		COUNT()			- the number of records in the group
		SUM(field_name)	- totals a specific field in the group
		MIN(field_name)	- lowest value of a field in the group
		MAX(field_name)	- highest value of a field in the group 
		AVG(field_name)	- averages a specific field in the group
		etc.
*/

-- aggregate functions summarize a group. without one specified, the group becomes the entire table
SELECT COUNT(*) FROM demo_orders;
SELECT COUNT(*) FROM demo_orders WHERE amount > 100;
SELECT SUM(amount) FROM demo_orders WHERE amount > 100; 
SELECT SUM(amount) FROM demo_orders;
SELECT MIN(amount) FROM demo_orders;
SELECT MAX(amount) FROM demo_orders;
SELECT AVG(amount) FROM demo_orders;

-- once you add a GROUP BY, the aggregate functions will summarize based on the groupings rather than the entire table
SELECT
	c.name, 
	COUNT(o.id) as order_count,
	SUM(o.amount) as total_spent
FROM demo_customers as c
LEFT JOIN demo_orders as o ON o.customer_id = c.id
GROUP BY c.name
ORDER BY total_spent DESC NULLS LAST;
























	