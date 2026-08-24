# SQL Assignment – Chinook Database

**Database:** PostgreSQL | **Schema:** Chinook

---

## Easy (Questions 1–3)

**1.** Retrieve the first name, last name, and email address of every customer in the database. Order the results alphabetically by last name.

**2.** List the name and unit price of all tracks that have a unit price greater than $0.99. Order by unit price descending.

**3.** Find the total number of tracks in the database.

---

## Medium (Questions 4–8)

**4.** List each customer's full name (first + last) alongside the total number of invoices they have. Only include customers who have placed **more than 3 invoices**. Order by invoice count descending.

**5.** Find the **top 5 most purchased tracks** (by quantity sold across all invoices). Display the track name and total quantity sold.

**6.** List all albums along with the name of the artist who made them and the **total number of tracks** on each album. Order by track count descending.

**7.** Find all customers who are located in the **same country as their assigned support representative** (sales agent). Return the customer's full name, the rep's full name, and the country.

**8.** Calculate the **total revenue generated per genre**. Display the genre name and total revenue, ordered by revenue descending.

---

## Hard (Questions 9–13)

**9.** Find the **month-over-month revenue** for the year 2021. Display the month number, month name, and total revenue for each month. *(Hint: use `TO_CHAR` or `DATE_PART`.)*

**10.** Identify customers who have **never purchased a track from the 'Rock' genre**. Return their full name and email.

**11.** For each country, find the **single highest-spending customer**. Display the country, the customer's full name, and their total spend. *(Hint: consider using `RANK()` or a subquery.)*

**12.** Find all tracks that have **never been purchased**. Display the track name, album title, and artist name.

**13.** List every employee and their **direct report chain up to the top-level manager**. Display the employee's name, their manager's name, and their manager's manager's name (if one exists). *(Hint: the `Employee` table has a `ReportsTo` self-referencing column — use self-joins.)*

---

## Advanced (Questions 14–15)

**14.** Write a query that assigns each customer a **spending tier** based on their total lifetime spend using a `CASE` expression:

| Tier | Condition |
|------|-----------|
| Platinum | Spent more than $45 |
| Gold | Spent between $30 and $45 |
| Silver | Spent between $15 and $30 |
| Bronze | Spent less than $15 |

Return the customer's full name, total spend, and tier. Order by total spend descending.

**15.** Using a **Common Table Expression (CTE)**, calculate the following for each artist:

- Total number of albums
- Total number of tracks across all albums
- Total revenue generated from all track sales

Only include artists who have generated **more than $30 in total revenue**. Order by total revenue descending.

---

*Good luck! Focus on writing clean, readable SQL — use aliases, consistent formatting, and comments where helpful.*
