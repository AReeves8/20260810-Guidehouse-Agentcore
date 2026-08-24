# Week 2 Assignment Solution: Chinook Database SQL Practice


**Trainees are not expected to produce the SQLAlchemy version on their
own**. It's included purely as extra reference for how the ORM works.


## Models used in the SQLAlchemy examples

Every SQLAlchemy snippet below assumes these declarative models already
exist (shown once here, not repeated per question) — the same
`Mapped`/`mapped_column` style `db_models.py` uses, just against Chinook's
tables instead of `tickets`/`ticket_comments`:

```python
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customer"
    customer_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    country: Mapped[str | None]
    support_rep_id: Mapped[int | None] = mapped_column(ForeignKey("employee.employee_id"))


class Employee(Base):
    __tablename__ = "employee"
    employee_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    country: Mapped[str | None]
    reports_to: Mapped[int | None] = mapped_column(ForeignKey("employee.employee_id"))


class Invoice(Base):
    __tablename__ = "invoice"
    invoice_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.customer_id"))
    invoice_date: Mapped[datetime]
    total: Mapped[float] = mapped_column(Numeric(10, 2))


class InvoiceLine(Base):
    __tablename__ = "invoice_line"
    invoice_line_id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.invoice_id"))
    track_id: Mapped[int] = mapped_column(ForeignKey("track.track_id"))
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    quantity: Mapped[int]


class Track(Base):
    __tablename__ = "track"
    track_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    album_id: Mapped[int | None] = mapped_column(ForeignKey("album.album_id"))
    genre_id: Mapped[int | None] = mapped_column(ForeignKey("genre.genre_id"))
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))


class Album(Base):
    __tablename__ = "album"
    album_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.artist_id"))


class Artist(Base):
    __tablename__ = "artist"
    artist_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None]


class Genre(Base):
    __tablename__ = "genre"
    genre_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None]
```

**Note on table/column names:** this solution uses the lowercase,
snake_case table names (`customer`, `invoice_line`, `support_rep_id`,
etc.) from the official PostgreSQL port of Chinook linked in
`ASSIGNMENT.md`. If your loaded copy uses different casing, adjust
accordingly — that's exactly why the assignment tells you to check your
actual schema first.

---

### Q1. Retrieve the first name, last name, and email address of every customer in the database. Order the results alphabetically by last name.

**SQL:**
```sql
SELECT first_name, last_name, email
FROM customer
ORDER BY last_name;
```

**SQLAlchemy:**
```python
stmt = (
    select(Customer.first_name, Customer.last_name, Customer.email)
    .order_by(Customer.last_name)
)
session.execute(stmt).all()
```

---

### Q2. List the name and unit price of all tracks that have a unit price greater than $0.99. Order by unit price descending.

**SQL:**
```sql
SELECT name, unit_price
FROM track
WHERE unit_price > 0.99
ORDER BY unit_price DESC;
```

**SQLAlchemy:**
```python
stmt = (
    select(Track.name, Track.unit_price)
    .where(Track.unit_price > 0.99)
    .order_by(Track.unit_price.desc())
)
session.execute(stmt).all()
```

---

### Q3. Find the total number of tracks in the database.

**SQL:**
```sql
SELECT COUNT(*) AS total_tracks
FROM track;
```

**SQLAlchemy:**
```python
stmt = select(func.count()).select_from(Track)
session.execute(stmt).scalar_one()
```

---

### Q4. List each customer's full name (first + last) alongside the total number of invoices they have. Only include customers who have placed more than 3 invoices. Order by invoice count descending.

**SQL:**
```sql
SELECT c.first_name || ' ' || c.last_name AS full_name,
       COUNT(i.invoice_id) AS invoice_count
FROM customer c
JOIN invoice i ON i.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(i.invoice_id) > 3
ORDER BY invoice_count DESC;
```

**SQLAlchemy:**
```python
stmt = (
    select(
        (Customer.first_name + " " + Customer.last_name).label("full_name"),
        func.count(Invoice.invoice_id).label("invoice_count"),
    )
    .join(Invoice, Invoice.customer_id == Customer.customer_id)
    .group_by(Customer.customer_id, Customer.first_name, Customer.last_name)
    .having(func.count(Invoice.invoice_id) > 3)
    .order_by(func.count(Invoice.invoice_id).desc())
)
session.execute(stmt).all()
```

---

### Q5. Find the top 5 most purchased tracks (by quantity sold across all invoices). Display the track name and total quantity sold.

**SQL:**
```sql
SELECT t.name, SUM(il.quantity) AS total_quantity
FROM track t
JOIN invoice_line il ON il.track_id = t.track_id
GROUP BY t.track_id, t.name
ORDER BY total_quantity DESC
LIMIT 5;
```

**SQLAlchemy:**
```python
stmt = (
    select(Track.name, func.sum(InvoiceLine.quantity).label("total_quantity"))
    .join(InvoiceLine, InvoiceLine.track_id == Track.track_id)
    .group_by(Track.track_id, Track.name)
    .order_by(func.sum(InvoiceLine.quantity).desc())
    .limit(5)
)
session.execute(stmt).all()
```

---

### Q6. List all albums along with the name of the artist who made them and the total number of tracks on each album. Order by track count descending.

**SQL:**
```sql
SELECT al.title AS album_title, ar.name AS artist_name, COUNT(t.track_id) AS track_count
FROM album al
JOIN artist ar ON ar.artist_id = al.artist_id
LEFT JOIN track t ON t.album_id = al.album_id
GROUP BY al.album_id, al.title, ar.name
ORDER BY track_count DESC;
```
`LEFT JOIN` to `track`, not `JOIN` — an album with zero tracks should
still appear (with a count of `0`), the same "keep every row from the
left table" reasoning behind this week's anti-join pattern, just without
the follow-up `WHERE ... IS NULL` filter this time.

**SQLAlchemy:**
```python
stmt = (
    select(
        Album.title.label("album_title"),
        Artist.name.label("artist_name"),
        func.count(Track.track_id).label("track_count"),
    )
    .join(Artist, Artist.artist_id == Album.artist_id)
    .outerjoin(Track, Track.album_id == Album.album_id)
    .group_by(Album.album_id, Album.title, Artist.name)
    .order_by(func.count(Track.track_id).desc())
)
session.execute(stmt).all()
```

---

### Q7. Find all customers who are located in the same country as their assigned support representative. Return the customer's full name, the rep's full name, and the country.

**SQL:**
```sql
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       e.first_name || ' ' || e.last_name AS rep_name,
       c.country
FROM customer c
JOIN employee e ON e.employee_id = c.support_rep_id
WHERE c.country = e.country;
```

**SQLAlchemy:**
```python
from sqlalchemy.orm import aliased

Rep = aliased(Employee)  # customer and employee are different roles here, not a self-join

stmt = (
    select(
        (Customer.first_name + " " + Customer.last_name).label("customer_name"),
        (Rep.first_name + " " + Rep.last_name).label("rep_name"),
        Customer.country,
    )
    .join(Rep, Rep.employee_id == Customer.support_rep_id)
    .where(Customer.country == Rep.country)
)
session.execute(stmt).all()
```

---

### Q8. Calculate the total revenue generated per genre. Display the genre name and total revenue, ordered by revenue descending.

**SQL:**
```sql
SELECT g.name AS genre_name, SUM(il.unit_price * il.quantity) AS total_revenue
FROM genre g
JOIN track t ON t.genre_id = g.genre_id
JOIN invoice_line il ON il.track_id = t.track_id
GROUP BY g.genre_id, g.name
ORDER BY total_revenue DESC;
```

**SQLAlchemy:**
```python
stmt = (
    select(
        Genre.name.label("genre_name"),
        func.sum(InvoiceLine.unit_price * InvoiceLine.quantity).label("total_revenue"),
    )
    .join(Track, Track.genre_id == Genre.genre_id)
    .join(InvoiceLine, InvoiceLine.track_id == Track.track_id)
    .group_by(Genre.genre_id, Genre.name)
    .order_by(func.sum(InvoiceLine.unit_price * InvoiceLine.quantity).desc())
)
session.execute(stmt).all()
```

---

### Q9. Find the month-over-month revenue for the year 2021. Display the month number, month name, and total revenue for each month.

**SQL:**
```sql
SELECT EXTRACT(MONTH FROM invoice_date)::int AS month_number,
       TO_CHAR(invoice_date, 'Month') AS month_name,
       SUM(total) AS total_revenue
FROM invoice
WHERE EXTRACT(YEAR FROM invoice_date) = 2021
GROUP BY month_number, month_name
ORDER BY month_number;
```

**SQLAlchemy:**
```python
month_number = func.extract("month", Invoice.invoice_date).label("month_number")
month_name = func.to_char(Invoice.invoice_date, "Month").label("month_name")

stmt = (
    select(month_number, month_name, func.sum(Invoice.total).label("total_revenue"))
    .where(func.extract("year", Invoice.invoice_date) == 2021)
    .group_by(month_number, month_name)
    .order_by(month_number)
)
session.execute(stmt).all()
```

---

### Q10. Identify customers who have never purchased a track from the 'Rock' genre. Return their full name and email.

**SQL:**
```sql
SELECT c.first_name || ' ' || c.last_name AS full_name, c.email
FROM customer c
LEFT JOIN (
    SELECT DISTINCT i.customer_id
    FROM invoice i
    JOIN invoice_line il ON il.invoice_id = i.invoice_id
    JOIN track t ON t.track_id = il.track_id
    JOIN genre g ON g.genre_id = t.genre_id
    WHERE g.name = 'Rock'
) rock_buyers ON rock_buyers.customer_id = c.customer_id
WHERE rock_buyers.customer_id IS NULL;
```

**Heads up — this genuinely returns zero rows.** Every single customer in
this dataset has bought at least one Rock track (confirmed: 59 out of 59).
An empty result set here is the *correct* answer, not a sign the query is
broken — the same lesson as this week's `NULL`/anti-join material: "nobody
matches" is a legitimate outcome to be able to recognize, not something to
assume means you made a mistake.

**SQLAlchemy:**
```python
rock_buyers = (
    select(Invoice.customer_id)
    .join(InvoiceLine, InvoiceLine.invoice_id == Invoice.invoice_id)
    .join(Track, Track.track_id == InvoiceLine.track_id)
    .join(Genre, Genre.genre_id == Track.genre_id)
    .where(Genre.name == "Rock")
    .distinct()
    .subquery()
)

stmt = (
    select((Customer.first_name + " " + Customer.last_name).label("full_name"), Customer.email)
    .outerjoin(rock_buyers, rock_buyers.c.customer_id == Customer.customer_id)
    .where(rock_buyers.c.customer_id.is_(None))
)
session.execute(stmt).all()  # returns [] against this dataset
```

---

### Q11. For each country, find the single highest-spending customer. Display the country, the customer's full name, and their total spend.

**SQL:**
```sql
SELECT country, full_name, total_spend
FROM (
    SELECT c.country,
           c.first_name || ' ' || c.last_name AS full_name,
           SUM(i.total) AS total_spend,
           RANK() OVER (PARTITION BY c.country ORDER BY SUM(i.total) DESC) AS spend_rank
    FROM customer c
    JOIN invoice i ON i.customer_id = c.customer_id
    GROUP BY c.country, c.customer_id, c.first_name, c.last_name
) ranked
WHERE spend_rank = 1
ORDER BY country;
```

**SQLAlchemy:**
```python
ranked = (
    select(
        Customer.country,
        (Customer.first_name + " " + Customer.last_name).label("full_name"),
        func.sum(Invoice.total).label("total_spend"),
        func.rank()
        .over(partition_by=Customer.country, order_by=func.sum(Invoice.total).desc())
        .label("spend_rank"),
    )
    .join(Invoice, Invoice.customer_id == Customer.customer_id)
    .group_by(Customer.country, Customer.customer_id, Customer.first_name, Customer.last_name)
    .subquery()
)

stmt = (
    select(ranked.c.country, ranked.c.full_name, ranked.c.total_spend)
    .where(ranked.c.spend_rank == 1)
    .order_by(ranked.c.country)
)
session.execute(stmt).all()
```
A window function can't go directly in `WHERE`/`HAVING` in either raw SQL
or SQLAlchemy — that's why both versions compute the rank in an inner
query/subquery first, then filter on it from the outside.

---

### Q12. Find all tracks that have never been purchased. Display the track name, album title, and artist name.

**SQL:**
```sql
SELECT t.name AS track_name, al.title AS album_title, ar.name AS artist_name
FROM track t
LEFT JOIN album al ON al.album_id = t.album_id
LEFT JOIN artist ar ON ar.artist_id = al.artist_id
LEFT JOIN invoice_line il ON il.track_id = t.track_id
WHERE il.invoice_line_id IS NULL;
```

**SQLAlchemy:**
```python
stmt = (
    select(Track.name.label("track_name"), Album.title.label("album_title"), Artist.name.label("artist_name"))
    .outerjoin(Album, Album.album_id == Track.album_id)
    .outerjoin(Artist, Artist.artist_id == Album.artist_id)
    .outerjoin(InvoiceLine, InvoiceLine.track_id == Track.track_id)
    .where(InvoiceLine.invoice_line_id.is_(None))
)
session.execute(stmt).all()
```

---

### Q13. (Advanced) List every employee's full reporting chain up to the top-level manager.

**SQL:**
```sql
WITH RECURSIVE chain AS (
    -- anchor: every employee, paired with themselves as the "current" node
    SELECT employee_id AS original_employee_id,
           employee_id AS current_id,
           reports_to AS current_reports_to,
           0 AS level
    FROM employee

    UNION ALL

    -- recursive step: walk from the current node up to ITS manager
    SELECT chain.original_employee_id,
           e.employee_id,
           e.reports_to,
           chain.level + 1
    FROM chain
    JOIN employee e ON e.employee_id = chain.current_reports_to
)
SELECT orig.first_name || ' ' || orig.last_name AS employee_name,
       mgr.first_name || ' ' || mgr.last_name AS manager_name,
       chain.level
FROM chain
JOIN employee orig ON orig.employee_id = chain.original_employee_id
JOIN employee mgr ON mgr.employee_id = chain.current_id
WHERE chain.level > 0
ORDER BY employee_name, level;
```
Reading this: the anchor row is "level 0 — every employee is their own
starting point." Each recursive pass joins back to `employee` to climb one
level higher, stopping naturally once `reports_to` is `NULL` (nothing left
to join to). The final `WHERE level > 0` just drops the "level 0" rows,
which would otherwise show every employee as their own manager.

**SQLAlchemy:**
```python
from sqlalchemy import literal
from sqlalchemy.orm import aliased

base = select(
    Employee.employee_id.label("original_employee_id"),
    Employee.employee_id.label("current_id"),
    Employee.reports_to.label("current_reports_to"),
    literal(0).label("level"),
).cte(name="chain", recursive=True)

Climb = aliased(Employee)
recursive_part = select(
    base.c.original_employee_id,
    Climb.employee_id,
    Climb.reports_to,
    base.c.level + 1,
).join(Climb, Climb.employee_id == base.c.current_reports_to)

chain = base.union_all(recursive_part)

Orig, Mgr = aliased(Employee), aliased(Employee)
stmt = (
    select(
        (Orig.first_name + " " + Orig.last_name).label("employee_name"),
        (Mgr.first_name + " " + Mgr.last_name).label("manager_name"),
        chain.c.level,
    )
    .join(Orig, Orig.employee_id == chain.c.original_employee_id)
    .join(Mgr, Mgr.employee_id == chain.c.current_id)
    .where(chain.c.level > 0)
    .order_by("employee_name", chain.c.level)
)
session.execute(stmt).all()
```
This is the most involved snippet in this solution by a wide margin — a
recursive CTE expressed through the ORM needs `.cte(recursive=True)`
followed by `.union_all(...)` to attach the recursive half, built as two
separate `select()`s rather than one. Trainees seeing this for the first
time should walk away recognizing the *shape*, not be expected to
reproduce it cold.

---

### Q14. (Advanced) Assign each customer a spending tier using a `CASE` expression.

**SQL:**
```sql
SELECT c.first_name || ' ' || c.last_name AS full_name,
       SUM(i.total) AS total_spend,
       CASE
           WHEN SUM(i.total) > 45 THEN 'Platinum'
           WHEN SUM(i.total) BETWEEN 30 AND 45 THEN 'Gold'
           WHEN SUM(i.total) BETWEEN 15 AND 30 THEN 'Silver'
           ELSE 'Bronze'
       END AS tier
FROM customer c
JOIN invoice i ON i.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spend DESC;
```
`CASE` evaluates top to bottom and stops at the first true condition, so
listing `Platinum` first and `Bronze` last (as `ELSE`) is what correctly
resolves the overlap at the exact boundaries ($30 and $45 both technically
satisfy two `BETWEEN`s) in favor of the higher tier.

**SQLAlchemy:**
```python
total_spend = func.sum(Invoice.total)
tier = case(
    (total_spend > 45, "Platinum"),
    (total_spend.between(30, 45), "Gold"),
    (total_spend.between(15, 30), "Silver"),
    else_="Bronze",
).label("tier")

stmt = (
    select(
        (Customer.first_name + " " + Customer.last_name).label("full_name"),
        total_spend.label("total_spend"),
        tier,
    )
    .join(Invoice, Invoice.customer_id == Customer.customer_id)
    .group_by(Customer.customer_id, Customer.first_name, Customer.last_name)
    .order_by(total_spend.desc())
)
session.execute(stmt).all()
```

---

### Q15. (Advanced) Using a CTE, calculate per-artist album count, track count, and total revenue; keep only artists earning more than $30.

**SQL:**
```sql
WITH artist_stats AS (
    SELECT ar.artist_id,
           ar.name AS artist_name,
           COUNT(DISTINCT al.album_id) AS total_albums,
           COUNT(DISTINCT t.track_id) AS total_tracks,
           COALESCE(SUM(il.unit_price * il.quantity), 0) AS total_revenue
    FROM artist ar
    LEFT JOIN album al ON al.artist_id = ar.artist_id
    LEFT JOIN track t ON t.album_id = al.album_id
    LEFT JOIN invoice_line il ON il.track_id = t.track_id
    GROUP BY ar.artist_id, ar.name
)
SELECT artist_name, total_albums, total_tracks, total_revenue
FROM artist_stats
WHERE total_revenue > 30
ORDER BY total_revenue DESC;
```
`COUNT(DISTINCT ...)` matters here — without it, an artist with 2 albums
and 10 tracks each would inflate to 20 counted "albums" once the joins
fan out to the track and invoice_line level. `COALESCE(..., 0)` covers an
artist with albums but zero sales, where `SUM` would otherwise return `NULL`.

**SQLAlchemy:**
```python
artist_stats = (
    select(
        Artist.artist_id,
        Artist.name.label("artist_name"),
        func.count(func.distinct(Album.album_id)).label("total_albums"),
        func.count(func.distinct(Track.track_id)).label("total_tracks"),
        func.coalesce(func.sum(InvoiceLine.unit_price * InvoiceLine.quantity), 0).label("total_revenue"),
    )
    .outerjoin(Album, Album.artist_id == Artist.artist_id)
    .outerjoin(Track, Track.album_id == Album.album_id)
    .outerjoin(InvoiceLine, InvoiceLine.track_id == Track.track_id)
    .group_by(Artist.artist_id, Artist.name)
    .cte("artist_stats")
)

stmt = (
    select(artist_stats.c.artist_name, artist_stats.c.total_albums, artist_stats.c.total_tracks, artist_stats.c.total_revenue)
    .where(artist_stats.c.total_revenue > 30)
    .order_by(artist_stats.c.total_revenue.desc())
)
session.execute(stmt).all()
```
