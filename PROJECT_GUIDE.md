# Air Tracker: Flight Analytics — Complete Project Guide

---

## Part 1: Is the Project Finished? Completion Checklist

Let's check every requirement from the project document against what we built.

### Core Requirements

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | Use AeroDataBox API (RapidAPI) for data extraction | Done | `ingest.py` — `fetch_and_load_api_data()` function |
| 2 | Store data in PostgreSQL (MySQL/PostgreSQL required) | Done | `schema.py` — PostgreSQL connection via `.env` |
| 3 | Create proper relational database schema (4 tables) | Done | `airport`, `aircraft`, `flights`, `airport_delays` tables |
| 4 | Write 11 mandatory SQL analytical queries | Done | `queries.sql` + `queries.py` |
| 5 | Build interactive Streamlit dashboard | Done | `app.py` — 6 pages with charts, maps, filters |
| 6 | All 11 queries return non-empty, correct results | Verified | Ran `python queries.py` — all 11 passed on PostgreSQL |

### SQL Concepts Covered (All 11 Queries)

| Query | SQL Concepts Used | Verified |
|---|---|---|
| Q1: Flights per Aircraft Model | `JOIN`, `GROUP BY`, `COUNT`, `ORDER BY` | Yes |
| Q2: Aircraft with >5 Flights | `JOIN`, `GROUP BY`, `HAVING`, `COUNT` | Yes |
| Q3: Airports with >5 Outbound | `JOIN`, `GROUP BY`, `HAVING`, `COUNT` | Yes |
| Q4: Top 3 Destinations | `JOIN`, `GROUP BY`, `ORDER BY`, `LIMIT` | Yes |
| Q5: Domestic vs International | `JOIN` (multiple), `CASE WHEN` | Yes |
| Q6: 5 Recent Arrivals at DEL | `JOIN`, `WHERE`, `ORDER BY DESC`, `LIMIT` | Yes |
| Q7: Airports with No Arrivals | `Subquery`, `NOT IN`, `DISTINCT` | Yes |
| Q8: Airline Status Summary | `GROUP BY`, `CASE WHEN` inside `SUM` (pivot) | Yes |
| Q9: Cancelled Flight Details | Multi-table `JOIN`, `WHERE` filter | Yes |
| Q10: City Pairs >2 Models | 3-table `JOIN`, `COUNT(DISTINCT)`, `HAVING` | Yes |
| Q11: Delay % per Destination | `CASE WHEN`, `SUM`, `ROUND`, percentage calc | Yes |

### Dashboard Pages

| Page | Features | Status |
|---|---|---|
| Dashboard Home | KPI cards, world map, pie chart, bar chart | Done |
| Search & Filter Flights | Text search, multi-select filters, data table | Done |
| Airport Details Viewer | Dropdown selector, info panel, map, departure/arrival tabs | Done |
| Delay Analysis | Bar chart with color gradient, statistics table | Done |
| Route Leaderboards | Busiest routes bar chart, most delayed hubs chart | Done |
| Mandatory SQL Queries | Query selector, raw SQL display, execute button, CSV download | Done |

### Project Files

| File | Purpose | Status |
|---|---|---|
| `requirements.txt` | Python dependencies | Done |
| `.env` | Configuration (API key, DB credentials) | Done |
| `.env.example` | Template for other users | Done |
| `schema.py` | Database schema (ORM models) | Done |
| `ingest.py` | Data ingestion (API) | Done |
| `queries.sql` | Raw SQL file with all 11 queries | Done |
| `queries.py` | Python wrappers to execute queries | Done |
| `app.py` | Streamlit dashboard | Done |

> **The project is COMPLETE.** Every requirement has been built, tested, and verified against PostgreSQL. You can confidently submit this.

---

## Part 2: What Exactly Did We Build?

### The Big Picture

Imagine you're an analyst at an airline company. You need to answer questions like:
- "Which aircraft model flies the most?"
- "Which airports have the worst delays?"
- "What are the busiest routes?"

To answer these, you need **data** -> stored in a **database** -> queried with **SQL** -> displayed on a **dashboard**.

That's exactly what this project is: **a complete data pipeline from API -> Database -> SQL Analysis -> Visual Dashboard.**

### The Architecture (How Everything Connects)

```
+------------------+     +--------------+     +------------------+     +------------------+
|  AeroDataBox     |     |              |     |                  |     |                  |
|  API (RapidAPI)  |---->|  ingest.py   |---->|   PostgreSQL     |---->|   Streamlit      |
|                  |     |              |     |   Database       |     |   Dashboard      |
|  (Data Source)   |     |  (ETL Script)|     |   (Data Store)   |     |   (Frontend)     |
+------------------+     +--------------+     +------------------+     +------------------+
                              |                       ^                        |
                              |                       |                        |
                         schema.py              queries.py               app.py
                     (defines tables)        (runs SQL queries)      (renders charts)
```

### In Simple Words

1. **`schema.py`** = The blueprint. It says "I want 4 tables: airports, aircraft, flights, and delays -- each with these columns."
2. **`ingest.py`** = The data loader. It fetches real flight data from the internet (API) using the AeroDataBox API.
3. **`queries.py`** = The analyst. It contains 11 SQL questions and runs them against the database.
4. **`app.py`** = The presentation. It takes the data and query results, and shows them as beautiful interactive charts and tables in a web browser.

---

## Part 3: Concepts You Learned

### 3.1 -- Python Virtual Environments (`venv`)

**What**: A virtual environment is an isolated Python installation. Packages you install inside it don't affect your global Python.

**Why**: Different projects need different versions of packages. Without venv, installing package X for Project A could break Project B.

**How we used it**:
```bash
python -m venv venv          # Create a folder called "venv" with its own Python
venv\Scripts\activate         # Switch to using that Python
pip install -r requirements.txt  # Install packages ONLY inside this environment
```

### 3.2 -- Environment Variables (`.env` files)

**What**: A `.env` file stores sensitive configuration (passwords, API keys) outside your code.

**Why**: You never want to hardcode passwords in your Python files. If you share code on GitHub, everyone would see your password.

**How we used it**:
```env
RAPIDAPI_KEY=96b9d76318msh...    # API key (secret)
DB_TYPE=postgresql                # Which database to use
DB_PASSWORD=Admin                 # Database password (secret)
```

In Python, we read these using:
```python
from dotenv import load_dotenv
import os

load_dotenv()                           # Read the .env file
api_key = os.getenv("RAPIDAPI_KEY")     # Get a specific value
```

### 3.3 -- REST APIs (AeroDataBox via RapidAPI)

**What**: An API is a URL you can call to get data. You send a request, and it sends back JSON data.

**How we used it**:
```python
import requests

headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': "aerodatabox.p.rapidapi.com"
}

# GET request to fetch airport data
response = requests.get(
    "https://aerodatabox.p.rapidapi.com/airports/iata/DEL",
    headers=headers
)

data = response.json()  # Parse the JSON response into a Python dictionary
print(data["name"])      # "Indira Gandhi International Airport"
```

**Key concept**: Every API call uses HTTP methods (`GET` to read data). The headers carry your authentication (API key).

### 3.4 -- SQLAlchemy ORM (Object-Relational Mapping)

**What**: Instead of writing raw SQL to create tables, you define Python classes. SQLAlchemy converts them to SQL automatically.

**Why**: Your Python classes work with SQLite, PostgreSQL, AND MySQL without changing a single line. The ORM translates for you.

**Example from our project**:
```python
class Airport(Base):
    __tablename__ = 'airport'                                    # Table name in database
    airport_id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing ID
    iata_code = Column(String(10), unique=True, nullable=False)  # Must be unique, can't be empty
    name = Column(String(255))                                    # Airport name
    latitude = Column(Float)                                      # Decimal number
```

This is equivalent to this raw SQL:
```sql
CREATE TABLE airport (
    airport_id SERIAL PRIMARY KEY,
    iata_code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255),
    latitude FLOAT
);
```

### 3.5 -- SQL Concepts (The Core of This Project)

#### JOIN -- Combining Tables
```sql
-- "Get flight number AND the aircraft model for each flight"
-- flights table has aircraft_registration, aircraft table has model
-- JOIN connects them using a shared column
SELECT f.flight_number, ac.model
FROM flights f
JOIN aircraft ac ON f.aircraft_registration = ac.registration;
```

Think of it like a VLOOKUP in Excel: "Look up the model from the aircraft table using the registration number."

#### GROUP BY + COUNT -- Aggregation
```sql
-- "How many flights does each aircraft model have?"
SELECT ac.model, COUNT(f.flight_id) AS flight_count
FROM flights f
JOIN aircraft ac ON f.aircraft_registration = ac.registration
GROUP BY ac.model;
```

This groups all rows with the same model together, then counts how many flights are in each group.

#### HAVING -- Filter AFTER Grouping
```sql
-- "Only show models with more than 5 flights"
GROUP BY ac.model
HAVING COUNT(f.flight_id) > 5;
```

`WHERE` filters individual rows BEFORE grouping. `HAVING` filters groups AFTER grouping.

#### CASE WHEN -- Conditional Labels
```sql
-- "Label each flight as Domestic or International"
CASE
    WHEN orig.country = dest.country THEN 'Domestic'
    ELSE 'International'
END AS flight_type
```

This is SQL's version of an if-else statement.

#### Subquery -- A Query Inside a Query
```sql
-- "Find airports that are NEVER a destination"
WHERE ap.iata_code NOT IN (
    SELECT DISTINCT f.destination_iata
    FROM flights f
    WHERE f.destination_iata IS NOT NULL
)
```

The inner query gets all destination airport codes. The outer query finds airports NOT in that list.

#### ROUND + Percentage Calculation
```sql
ROUND(
    (SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) * 100.0) / COUNT(f.flight_id),
    2
) AS delay_percentage
```

- `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` -- counts how many rows match a condition
- `* 100.0` -- convert to percentage (the `.0` forces decimal division, not integer division)
- `ROUND(..., 2)` -- round to 2 decimal places

### 3.6 -- Streamlit (Dashboard Framework)

**What**: Streamlit lets you build web dashboards using only Python. No HTML/CSS/JavaScript needed.

**Key patterns we used**:

```python
import streamlit as st

# Page configuration
st.set_page_config(page_title="Air Tracker", layout="wide")

# Sidebar navigation
page = st.sidebar.radio("Navigate:", ["Home", "Search", "Details"])

# Conditional page rendering
if page == "Home":
    st.title("Dashboard Home")
    # ... home page content
elif page == "Search":
    st.title("Search Flights")
    # ... search page content

# Interactive widgets
search = st.text_input("Search:")              # Text box
selected = st.selectbox("Pick one:", options)   # Dropdown
filters = st.multiselect("Filter:", options)    # Multi-select

# Display data
st.dataframe(my_dataframe)                      # Interactive table

# Caching (so data isn't reloaded every click)
@st.cache_data(ttl=60)
def load_data():
    return pd.read_sql_table("flights", engine)
```

### 3.7 -- Plotly (Interactive Charts)

```python
import plotly.express as px

# Pie chart
fig = px.pie(data, values='Count', names='Status', hole=0.4)

# Bar chart
fig = px.bar(data, x='Airline', y='Flights', color='Flights')

# Map
fig = px.scatter_mapbox(data, lat="latitude", lon="longitude",
                        hover_name="name", zoom=1)
fig.update_layout(mapbox_style="carto-darkmatter")

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)
```

### 3.8 -- Pandas (Data Manipulation)

```python
import pandas as pd

# Read SQL into DataFrame
df = pd.read_sql_table("flights", engine)
df = pd.read_sql_query("SELECT * FROM flights", connection)

# Filter rows
delayed = df[df['status'] == 'Delayed']

# String search
matches = df[df['flight_number'].str.contains("AI", case=False)]

# Aggregation
counts = df['status'].value_counts()

# Merge (like SQL JOIN in Python)
merged = pd.merge(delays_df, airports_df, left_on="airport_iata", right_on="iata_code")
```

---

## Part 4: File-by-File Code Walkthrough

### File 1: `schema.py` -- The Database Blueprint

This file does 3 things:
1. Defines what tables exist and what columns they have
2. Builds the database connection URL based on your `.env` settings
3. Creates the tables and returns a session to interact with them

**Key logic flow**:
```
load_dotenv()  ->  Read .env file
                       |
get_db_url()   ->  Build connection string like "postgresql://postgres:Admin@localhost:5432/flight_analytics"
                       |
get_engine()   ->  Create SQLAlchemy engine (a reusable connection pool)
                       |
init_db()      ->  1. Auto-create database if it doesn't exist (PostgreSQL only)
                   2. Create all tables defined by the ORM classes
                   3. Return a Session object for inserting/querying data
```

---

### File 2: `ingest.py` -- The Data Loader

This script coordinates the entire database loading process using the AeroDataBox API:

**API Ingestion flow** (`python ingest.py`):
```
Start -> init_db() -> Create tables
  -> For each of 12 airports:
      -> Call API: GET /airports/iata/{code} -> Insert airport data
  -> For first 4 airports:
      -> Call API: GET /flights/airports/iata/{code}/{start}/{end} -> Parse flights
  -> For each unique aircraft registration found in flights:
      -> Call API: GET /aircrafts/reg/{registration} -> Insert aircraft data
  -> For each airport:
      -> Call API: GET /airports/iata/{code}/delays -> Insert delay stats
  -> On any API failure -> Insert fallback/default data
```

---

### File 3: `queries.py` -- The SQL Runner

Structure:
```python
QUERIES = [
    {
        "id": 1,
        "title": "1) Total Flights per Aircraft Model",
        "description": "...",
        "sql": "SELECT ac.model, COUNT(f.flight_id) ..."
    },
    # ... 10 more queries
]

def run_query(query_id):
    # 1. Find the query object by ID
    query_obj = next((q for q in QUERIES if q["id"] == query_id), None)
    # 2. Connect to database
    engine = get_engine()
    # 3. Execute the SQL and return results as a Pandas DataFrame
    with engine.connect() as conn:
        df = pd.read_sql_query(query_obj["sql"], conn)
    return df
```

The `next()` function with a generator expression is a Pythonic way to find the first matching item in a list. It's like saying "give me the first query where id equals query_id."

---

### File 4: `app.py` -- The Dashboard

**Architecture**:
```
1. Configure page (title, layout, icon)
2. Inject custom CSS for styling
3. Load all 4 tables into DataFrames (cached)
4. Build sidebar navigation
5. Based on selected page -> render that page's content
6. Render footer
```

**The page routing pattern**:
```python
page = st.sidebar.radio("Navigate:", ["Page1", "Page2", ...])

if page == "Page1":
    # render page 1
elif page == "Page2":
    # render page 2
# ... etc
```

**The caching pattern** (`@st.cache_data`):
```python
@st.cache_data(ttl=60)  # Cache results for 60 seconds
def load_table_data(table_name):
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_table(table_name, conn)
    return df
```

Without caching, every time you click a button or filter, Streamlit re-runs the entire script, which would mean re-querying the database every time. `@st.cache_data` remembers the result and reuses it.

---

## Part 5: How to Reproduce This Project From Scratch

If you had to build this yourself from zero, here's the exact order:

### Step 1: Setup (5 min)
```bash
mkdir "flight analytics"
cd "flight analytics"
python -m venv venv
venv\Scripts\activate
```
Create `requirements.txt` with: streamlit, pandas, plotly, requests, python-dotenv, sqlalchemy, psycopg2-binary
```bash
pip install -r requirements.txt
```

### Step 2: Create `.env` (2 min)
```env
RAPIDAPI_KEY=your_key_here
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=flight_analytics
DB_USER=postgres
DB_PASSWORD=your_password
```

### Step 3: Write `schema.py` (15 min)
1. Import SQLAlchemy's `Column`, `Integer`, `String`, `Float`, `create_engine`, `declarative_base`
2. Create `Base = declarative_base()`
3. Define 4 classes: `Airport`, `Aircraft`, `Flight`, `AirportDelay` -- each with `__tablename__` and `Column` definitions
4. Write `get_db_url()` -- reads `.env` and builds the connection string
5. Write `get_engine()` -- calls `create_engine(url)`
6. Write `init_db()` -- calls `Base.metadata.create_all(engine)` and returns a `Session`

### Step 4: Write `ingest.py` (30 min)
1. Define hardcoded airport metadata as list of dictionaries (for fallbacks/API queries)
2. Write `fetch_and_load_api_data(session, api_key)` -- calls `requests.get()` to the AeroDataBox endpoints, parses JSON, creates ORM objects
3. Write `main()` to load the database using the API key from environment variables

### Step 5: Write `queries.sql` and `queries.py` (20 min)
1. Write the 11 SQL queries covering JOIN, GROUP BY, HAVING, CASE WHEN, subquery, LIMIT
2. In `queries.py`, store them as a list of dictionaries
3. Write `run_query(id)` that uses `pd.read_sql_query()`

### Step 6: Write `app.py` (45 min)
1. `st.set_page_config()` and custom CSS
2. Load data with `@st.cache_data`
3. Sidebar radio for page navigation
4. For each page: use `st.columns()` for layout, Plotly for charts, `st.dataframe()` for tables
5. For the SQL queries page: `st.selectbox` for query selection, `st.button` to execute, `st.download_button` for CSV

### Step 7: Run and Test (10 min)
```bash
python ingest.py             # Load API data
python queries.py             # Verify all 11 queries
streamlit run app.py          # Launch dashboard
```

---

## Part 6: Key Takeaways

| Concept | What You Learned |
|---|---|
| **ETL Pipeline** | Extract data from API -> Transform/parse JSON -> Load into database |
| **Relational Database Design** | Designing normalized tables with proper primary/foreign key relationships |
| **SQL Mastery** | JOIN, GROUP BY, HAVING, CASE WHEN, subqueries, aggregations, LIMIT, ORDER BY |
| **ORM Pattern** | Define database schema as Python classes instead of raw SQL |
| **Environment Management** | venv for isolation, .env for secrets, requirements.txt for dependencies |
| **API Integration** | HTTP requests, JSON parsing, headers/authentication, error handling |
| **Dashboard Building** | Streamlit pages, sidebar navigation, interactive widgets, caching |
| **Data Visualization** | Plotly charts (pie, bar, scatter_mapbox), color scales, layout customization |
| **Data Analysis** | Pandas DataFrames, filtering, merging, value_counts, string operations |
| **Error Handling** | try/except blocks, graceful fallbacks when API fails |

> **For your viva/presentation**: Focus on explaining the SQL queries and the architecture diagram. These are the most commonly asked questions. Be ready to explain what each SQL keyword does (JOIN, GROUP BY, HAVING, CASE WHEN, subquery) and why you chose PostgreSQL over SQLite.
