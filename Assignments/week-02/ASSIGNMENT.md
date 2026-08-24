# Week 2 Assignment: Chinook Database SQL Practice

## What this reinforces
This week covered SQL fundamentals and relational modeling, JOINs, and
aggregate functions with `GROUP BY` (Thursday), all applied against the
`ticket_api` project's own schema. This assignment steps away from that
project and puts the same skills to work against a different, unfamiliar
schema — Chinook, a sample digital-music-store database — through a set of
progressively harder scenarios: simple lookups, then JOINs and aggregation,
then two techniques (CTEs and window functions) this week's demos didn't
cover directly. Figuring out how to apply a new SQL technique from
documentation is a normal, ongoing part of writing SQL professionally, not
something you're expected to already know cold.

## Objective
Answer every required scenario below with a single, correct PostgreSQL
query, run against a live Chinook database, and confirm each one actually
returns the shape of result the scenario describes.

## Database
Use the [Chinook sample database](https://github.com/lerocha/chinook-database/blob/master/ChinookDatabase/DataSources/Chinook_PostgreSql_AutoIncrementPKs.sql)
— a small, well-known dataset modeling a digital music store (artists,
albums, tracks, genres, customers, employees, and invoices). That
repository includes a PostgreSQL-specific version of the schema and data;
load that into a local Postgres database before starting.

**Table and column names vary slightly between community ports of this
dataset** — inspect your actual schema first (`\d` at the `psql` prompt, or
pgAdmin's schema browser) rather than assuming exact casing/naming from the
scenarios below. Adjust identifiers to match what you actually loaded.

## Requirements

**Only the first 12 scenarios are required.** The final 3 (Advanced) are
optional extra practice — attempt them if you finish early or want the
extra challenge, but they don't affect whether this assignment is complete.

For any scenario that calls for a **Common Table Expression (CTE)** or a
**window function** — neither was covered directly in this week's
demos — a documentation link is included at that scenario. Read it, then
work out how to apply it to the specific question.

### Easy (Questions 1–3) — required

1. Retrieve the first name, last name, and email address of every customer in the database. Order the results alphabetically by last name.
2. List the name and unit price of all tracks that have a unit price greater than $0.99. Order by unit price descending.
3. Find the total number of tracks in the database.

### Medium (Questions 4–8) — required

4. List each customer's full name (first + last) alongside the total number of invoices they have. Only include customers who have placed **more than 3 invoices**. Order by invoice count descending.
5. Find the **top 5 most purchased tracks** (by quantity sold across all invoices). Display the track name and total quantity sold.
6. List all albums along with the name of the artist who made them and the **total number of tracks** on each album. Order by track count descending.
7. Find all customers who are located in the **same country as their assigned support representative** (sales agent). Return the customer's full name, the rep's full name, and the country.
8. Calculate the **total revenue generated per genre**. Display the genre name and total revenue, ordered by revenue descending.

### Hard (Questions 9–12) — required

9. Find the **month-over-month revenue** for the year 2021. Display the month number, month name, and total revenue for each month. *(Hint: use `TO_CHAR` or `DATE_PART`.)*
10. Identify customers who have **never purchased a track from the 'Rock' genre**. Return their full name and email. *(Hint: this is the same `LEFT JOIN` + `IS NULL` anti-join shape from this week's demo — a plain `INNER JOIN` can't express "this never happened.")*
11. For each country, find the **single highest-spending customer**. Display the country, the customer's full name, and their total spend. *(A clean way to do this is a window function — `RANK()` or `ROW_NUMBER()` with `PARTITION BY` — though a subquery can also get you there. If you go the window-function route: [PostgreSQL's window functions tutorial](https://www.postgresql.org/docs/current/tutorial-window.html) and the [window function reference](https://www.postgresql.org/docs/current/functions-window.html).)*
12. Find all tracks that have **never been purchased**. Display the track name, album title, and artist name.

### Advanced (Questions 13–15) — optional, extra practice

13. List every employee's **full reporting chain up to the top-level manager** — however many levels that takes, not just one or two fixed levels. Display the employee's name and the name of every manager above them, from their direct manager up to whoever has no manager at all. *(The employee table has a self-referencing "reports to" column. A chain of unknown depth like this needs a **recursive CTE** — a `WITH RECURSIVE` query that starts from each employee and repeatedly joins back to the same table until it runs out of managers. Reference: [PostgreSQL `WITH` queries, including the recursive form](https://www.postgresql.org/docs/current/queries-with.html).)*
14. Write a query that assigns each customer a **spending tier** based on their total lifetime spend using a `CASE` expression:

    | Tier | Condition |
    |------|-----------|
    | Platinum | Spent more than $45 |
    | Gold | Spent between $30 and $45 |
    | Silver | Spent between $15 and $30 |
    | Bronze | Spent less than $15 |

    Return the customer's full name, total spend, and tier. Order by total spend descending.

15. Using a **Common Table Expression (CTE)**, calculate the following for each artist:
    - Total number of albums
    - Total number of tracks across all albums
    - Total revenue generated from all track sales

    Only include artists who have generated **more than $30 in total revenue**. Order by total revenue descending. *(Reference: [PostgreSQL `WITH` queries](https://www.postgresql.org/docs/current/queries-with.html).)*

## Deliverable
A single `.sql` file containing one query per scenario you complete (all 12
required, plus any of the 3 Advanced ones you attempt), each preceded by a
comment noting which question it answers, pushed to a **public GitHub
repository** — submit the repository URL on Canvas, nothing else.

Your repo must:
- Include a short `README.md` noting which Postgres version and which
  Chinook script/version you loaded and tested against.
- Have every required query run without error against a fresh load of the
  Chinook database and return the shape of result the scenario describes.

## Time expectation
~2 hours for the 12 required scenarios. The 3 Advanced questions are
open-ended extra practice — budget additional time only if you attempt them.
