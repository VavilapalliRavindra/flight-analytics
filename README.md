# Air Tracker: Flight Analytics

A complete data pipeline for aviation analytics — from API data extraction to SQL analysis to interactive dashboard.

## Project Overview

```
AeroDataBox API  →  ingest.py  →  PostgreSQL  →  queries.py  →  Streamlit Dashboard
   (source)         (ETL)        (storage)       (analysis)       (visualization)
```

---

## Prerequisites (Install These First)

### 1. Python 3.10+ 
Download from https://www.python.org/downloads/
During installation, **CHECK "Add Python to PATH"**.

Verify:
```bash
python --version
```

### 2. PostgreSQL 15+
Download from https://www.postgresql.org/download/
During installation:
- Set password for `postgres` user (remember this!)
- Keep default port `5432`
- After install, make sure the PostgreSQL service is running

Verify:
```bash
psql -U postgres -c "SELECT version();"
```

### 3. Git (optional, for cloning)
Download from https://git-scm.com/downloads

---

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd "flight analytics"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Create a file named `.env` in the project root (copy from `.env.example`):
```bash
copy .env.example .env
```

Edit `.env` with your actual values:
```env
RAPIDAPI_KEY=your_rapidapi_key_here
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=flight_analytics
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
```

**How to get the RapidAPI key:**
1. Go to https://rapidapi.com/
2. Create a free account
3. Search for "AeroDataBox"
4. Subscribe to the free tier
5. Copy the `X-RapidAPI-Key` from the API playground

### Step 6: Load Data into Database
```bash
python ingest.py
```
This script initializes the database tables (if they do not already exist) and populates them by fetching live flight schedules, airport info, and delay statistics from the AeroDataBox API.


### Step 7: Verify SQL Queries
```bash
python queries.py
```
All 11 queries should return non-empty results.

### Step 8: Launch Dashboard
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

---

## Project Structure

```
flight analytics/
├── .env                 # YOUR secrets (API key, DB password) — DO NOT push to Git
├── .env.example         # Template for .env (safe to push)
├── .gitignore           # Tells Git to ignore .env, venv, etc.
├── requirements.txt     # Python dependencies
├── schema.py            # Database schema (4 tables) using SQLAlchemy ORM
├── ingest.py            # Data extraction and pipeline loader from API
├── queries.sql          # All 11 SQL queries (standalone file)
├── queries.py           # Python wrappers to execute the 11 queries
├── app.py               # Streamlit dashboard (6 pages)
├── PROJECT_GUIDE.md     # Detailed project explanation and tutorial
└── README.md            # This file
```

## Database Tables

| Table | Description |
|-------|-------------|
| `airport` | 12 major airports with coordinates, timezone, country |
| `aircraft` | Aircraft registrations with model, manufacturer, owner |
| `flights` | Flight records with origin, destination, times, status |
| `airport_delays` | Delay statistics per airport per day |

## SQL Queries Implemented

1. Total flights per aircraft model
2. Aircraft with more than 5 flights
3. Airports with more than 5 outbound flights
4. Top 3 destination airports by arrivals
5. Domestic vs International flight classification
6. 5 most recent arrivals at DEL
7. Airports with no arriving flights
8. Airline flights by status summary
9. Cancelled flights details
10. City pairs with more than 2 aircraft models
11. Delay percentage per destination airport

## Dashboard Pages

1. **Homepage** — KPI cards, world map, status pie chart, airline bar chart
2. **Search & Filter** — Search flights by number, filter by status/airline
3. **Airport Details** — Select airport, view info panel + map + flights
4. **Delay Analysis** — Delay bar chart with color gradient + stats table
5. **Route Leaderboards** — Top 10 busiest routes, most delayed airports
6. **SQL Queries** — Execute any of the 11 queries, view results, download CSV

## Tech Stack

- **Language**: Python 3
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **API**: AeroDataBox (via RapidAPI)
- **Dashboard**: Streamlit
- **Charts**: Plotly
- **Data**: Pandas

## Troubleshooting

### "No RAPIDAPI_KEY found"
Make sure your `.env` file exists and has the correct key configured. An API key is required to load the live data.

### PostgreSQL connection refused
Make sure PostgreSQL service is running:
- Windows: Open Services (services.msc) → find "postgresql" → Start

### "Module not found" errors
Make sure your virtual environment is activated (`(venv)` in terminal) and run:
```bash
pip install -r requirements.txt
```
