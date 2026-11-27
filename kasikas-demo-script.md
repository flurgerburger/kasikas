# Kasikas — Video Demo Script & Speaker Notes
### JOIN · SUBQUERY · Database Verification

> **Format guide**
> - `[ACTION]` — something you do on screen
> - **Bold** — emphasis when speaking
> - *(italic)* — private note to yourself, don't read aloud
> - Lines are short on purpose — read naturally, pause between them.

---

## ▶ INTRO  *(~30 seconds)*

---

> "Hey — in this demo I'm going to walk through two database features I built into **Kasikas**, a Django web app for booking indie film screenings in Cebu."

> "The app is connected to a **Supabase PostgreSQL** database, and I'm going to show you two things:"

> "First, a **SQL JOIN** — where Django pulls data from two tables in a single query."

> "And second, a **SQL Subquery** — where an inner SELECT filters the results of an outer SELECT, all inside the database."

> "Then I'll flip over to Supabase and show you the actual rows that back all of this up."

> "Let's get into it."

---

## PART 1 — LEFT OUTER JOIN  *(~2.5 minutes)*

---

### 1-A · Set the scene

`[ACTION]` *Open VS Code. Show `accounts/models.py`. Scroll to the `Ticket` model.*

> "Quick look at the data model. We have two tables that matter here."

> "The first is **`accounts_film`** — it stores every film: the title, director, venue, ticket price, all of that."

> "The second is **`accounts_ticket`** — every time a user books a pass, a row gets written here."

`[ACTION]` *Point to `film = models.ForeignKey(Film, ...)` on line 53.*

> "That `film` field is a **Foreign Key** — it stores the `film_id` that links each ticket back to the film it belongs to."

> "So the relationship is: **one film can have many tickets**. That's the join we're going to see."

---

### 1-B · Open the view code

`[ACTION]` *Switch to `accounts/views.py`. Scroll to `film_detail()`.*

> "Here's the view that powers the film detail page."

> "Instead of a plain `.get()`, I'm calling `.annotate()` on the Film queryset — passing in `Count` and `Sum` from Django's ORM."

`[ACTION]` *Highlight the `annotate(total_bookings=Count('tickets'), total_seats=Sum('tickets__seats'))` lines.*

> "`Count('tickets')` tells Django — for each film, count how many ticket rows point to it."

> "`Sum('tickets__seats')` adds up the total seats across all those tickets."

> "Django sees those two aggregations and knows it needs to **join** the ticket table onto the film table to compute them."

---

### 1-C · Show the SQL

`[ACTION]` *Switch to the shell terminal. Paste and run Block A from the cheat sheet.*

```python
from accounts.models import Film
from django.db.models import Count, Sum

qs = Film.objects.annotate(
    total_bookings=Count('tickets'),
    total_seats=Sum('tickets__seats'),
).filter(pk=1)

print(qs.query)
```

`[ACTION]` *Let the SQL print. Scroll to highlight the JOIN line.*

> "And there it is — the raw SQL that Django sent to PostgreSQL."

> "Look at this part right here:"

> "`LEFT OUTER JOIN accounts_ticket ON accounts_film.id = accounts_ticket.film_id`"

> "That is a real SQL JOIN — **not** a Python loop, not two separate queries. One round trip to the database."

`[ACTION]` *Point to `COUNT(...)` and `SUM(...)` in the SELECT clause.*

> "And the `COUNT` and `SUM` are computed **inside** PostgreSQL — the aggregated numbers come back already calculated."

> "`LEFT OUTER JOIN` specifically means: even films with **zero** bookings still show up — their count just comes back as zero. No film gets dropped from the results."

---

### 1-D · Show the live page

`[ACTION]` *Open browser. Navigate to `http://127.0.0.1:8000/films/1/`.*

> "Now let's see this in the actual app."

> "This is the detail page for **Mga Dalan sa Gabii** — film number one."

`[ACTION]` *Scroll to the sidebar booking card. Point to the PASSES SOLD and SEATS RESERVED values.*

> "Right here in the sidebar — **PASSES SOLD: 3** and **SEATS RESERVED: 3**."

> "Those numbers were not hardcoded. They came from the JOIN — Django counted the rows in `accounts_ticket` where `film_id` equals this film's id."

`[ACTION]` *Navigate to `http://127.0.0.1:8000/films/2/`.*

> "Let's check another film — **Asin ug Hangin**."

> "This one has **1 pass sold**, **1 seat reserved** — a different count, pulled live from the same join query."

---

## PART 2 — SUBQUERY  *(~2.5 minutes)*

---

### 2-A · Set the scene

`[ACTION]` *Switch back to `accounts/views.py`. Scroll to `home()`.*

> "Now for the subquery — and this one lives in the **home view**."

> "The goal is: when a user is logged in, the home page should show them **only the films they've already booked** — a personalised 'Your Reel' section."

> "The challenge is doing that **without** loading every ticket into Python and looping through them."

> "Instead, we let the database do the filtering — using a **nested SELECT**."

---

### 2-B · Explain inner and outer query

`[ACTION]` *Highlight the `booked_film_ids` lines.*

> "Here's the **inner query**."

> "`Ticket.objects.filter(user=request.user).values('film_id')`"

> "This targets the `accounts_ticket` table and says: give me the `film_id` column — but only for tickets that belong to the **currently logged-in user**."

> "On its own, that's just a list of IDs. But we don't run it yet."

`[ACTION]` *Highlight the `Film.objects.filter(id__in=Subquery(...))` line.*

> "Here's the **outer query**."

> "We ask Django to fetch films — but filter using `id__in=Subquery(...)`, passing the inner query in directly."

> "Django wraps that inner queryset in a SQL `SELECT` and drops it straight into the `WHERE` clause of the outer query."

> "No Python. No list. The whole thing runs **inside PostgreSQL as a single statement**."

---

### 2-C · Show the SQL

`[ACTION]` *Switch to the shell terminal. Paste and run Block B.*

```python
from accounts.models import Film, Ticket
from django.db.models import Subquery
from django.contrib.auth.models import User

user = User.objects.get(username='ADMIN')
inner = Ticket.objects.filter(user=user).values('film_id')
outer = Film.objects.filter(id__in=Subquery(inner))

print(outer.query)
```

`[ACTION]` *Let the SQL print. Point to the WHERE clause.*

> "Look at the `WHERE` clause."

> "`WHERE accounts_film.id IN ( SELECT film_id FROM accounts_ticket WHERE user_id = 1 )`"

> "That is a **nested SELECT** — a query inside a query. The inner SELECT runs first, produces a set of film IDs, and the outer SELECT uses that set to filter the films it returns."

`[ACTION]` *Point to `"U0"` alias in the printed SQL.*

> "Django aliased the inner table as `U0` — that's just its internal naming convention for subquery tables. It doesn't change how the SQL works."

---

### 2-D · Show the live page

`[ACTION]` *Open browser. Go to `http://127.0.0.1:8000/`. Make sure you are logged out first.*

> "Home page, logged out. Notice there's **no 'Your Reel' section** — the template hides it completely when no user is authenticated."

`[ACTION]` *Log in as ADMIN. Reload the home page.*

> "Now logged in as **ADMIN** — and there it is."

`[ACTION]` *Scroll to the 'YOUR REEL' section. Point to the film pills.*

> "The **YOUR REEL** section appears, showing only the films this user has actually booked — **Mga Dalan sa Gabii** and **Asin ug Hangin**."

> "Every other film on the platform is filtered out — not by Python, but by that nested SQL SELECT we just saw in the terminal."

`[ACTION]` *Point to the dev server terminal in the background showing the printed SQL.*

> "And the server terminal is printing the same SQL live — every time this page loads for a logged-in user."

---

## PART 3 — SUPABASE DATABASE VERIFICATION  *(~2 minutes)*

---

### 3-A · Open Supabase

`[ACTION]` *Switch to browser tab with Supabase. Navigate to Table Editor.*

> "Now let's verify this in Supabase — the actual PostgreSQL database backing all of this."

> "I'll show you the rows that produced those numbers, so you can see the data and the Django output line up exactly."

---

### 3-B · accounts_film table

`[ACTION]` *Click on `accounts_film` table. Show the full list of rows.*

> "Here's the **`accounts_film`** table — the **main table** in our JOIN."

> "Every film has an `id` as its **Primary Key** — that `id` is what the other table joins onto."

`[ACTION]` *Click on the row for id = 1 (Mga Dalan sa Gabii).*

> "Film id `1` is **Mga Dalan sa Gabii**. Remember the sidebar showed **3 passes sold** for this one."

---

### 3-C · accounts_ticket table — prove the JOIN

`[ACTION]` *Navigate to `accounts_ticket` table. Filter rows by `film_id = 1`.*

> "Now the **`accounts_ticket`** table — the **related table** in our JOIN."

> "Filter by `film_id = 1`..."

`[ACTION]` *Show the filtered results — 3 rows.*

> "Three rows — each one a booking for **Mga Dalan sa Gabii**."

> "The `film_id` column in every row **equals** the `id` from `accounts_film`. That is the **Foreign Key** relationship — and that's the exact column Django used in the `ON` clause of the JOIN."

> "`ON accounts_film.id = accounts_ticket.film_id` — right there in the data."

`[ACTION]` *Point to the `seats` column values.*

> "Add up the `seats` column — 1 plus 1 plus 1 equals **3**. That's exactly the `SUM` the JOIN computed, and exactly what appeared in the sidebar."

---

### 3-D · accounts_ticket table — prove the SUBQUERY

`[ACTION]` *Clear the film_id filter. Filter by `user_id = 1`.*

> "Now let's verify the subquery. Filter by `user_id = 1` — that's the **ADMIN** user."

`[ACTION]` *Show the filtered rows — tickets for film_id 1 and film_id 2.*

> "Two distinct `film_id` values come back — `1` and `2`."

> "That is exactly what the **inner SELECT** returned — the set of film IDs that ADMIN has tickets for."

`[ACTION]` *Go back to the browser. Show the YOUR REEL section on the home page.*

> "And those two IDs map to exactly the two films in the **YOUR REEL** section — **Mga Dalan sa Gabii** and **Asin ug Hangin**."

> "The outer query used that result set to filter the full Film table — and only those two came through."

---

### 3-E · Schema view *(optional but powerful)*

`[ACTION]` *Navigate to Supabase → Database → Schema (or the visual schema diagram).*

> "One last thing — the schema visualizer makes the relationships really clear."

`[ACTION]` *Point to the arrow from `accounts_ticket.film_id` → `accounts_film.id`.*

> "This arrow is the **Foreign Key** — `film_id` in the ticket table points to `id` in the film table. The JOIN travels along this arrow."

`[ACTION]` *Point to the arrow from `accounts_ticket.user_id` → `auth_user.id`.*

> "And this arrow connects tickets to users. The Subquery's inner SELECT filters along **this** one — it asks: 'which film_ids have a ticket where user_id equals this user?'"

> "`accounts_ticket` is the **bridge table** — it connects users to films, and both of our queries use it in different directions."

---

## ▶ OUTRO  *(~20 seconds)*

---

> "So to recap — a **JOIN** combines columns from two tables in a single query, using a shared key. A **Subquery** lets the result of one SELECT drive the filtering of another."

> "Both run entirely inside PostgreSQL — no extra round trips, no Python loops — and Django's ORM writes the SQL for us from clean, readable Python."

> "That's it — thanks for watching."

---

## 📋 Pre-Recording Checklist

| | Task |
|---|---|
| ☐ | `runserver` running in Terminal 1 |
| ☐ | Shell open in Terminal 2 (for SQL blocks) |
| ☐ | Browser logged in as **ADMIN** |
| ☐ | Supabase Table Editor open in a tab |
| ☐ | `views.py` SQL DEBUG `print()` lines still present |
| ☐ | VS Code showing `models.py` as opening shot |
| ☐ | Screen recording software running |
