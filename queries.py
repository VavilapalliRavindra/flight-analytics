import pandas as pd
from schema import get_engine

# List of queries with their names, description, and raw SQL
QUERIES = [
    {
        "id": 1,
        "title": "1) Total Flights per Aircraft Model",
        "description": "Show the total number of flights for each aircraft model, listing the model and its count.",
        "sql": """
        SELECT 
            ac.model, 
            COUNT(f.flight_id) AS flight_count
        FROM flights f
        JOIN aircraft ac ON f.aircraft_registration = ac.registration
        GROUP BY ac.model
        ORDER BY flight_count DESC;
        """
    },
    {
        "id": 2,
        "title": "2) Aircraft Assigned to > 5 Flights",
        "description": "List all aircraft (registration, model) that have been assigned to more than 5 flights.",
        "sql": """
        SELECT 
            ac.registration, 
            ac.model,
            COUNT(f.flight_id) AS flight_count
        FROM aircraft ac
        JOIN flights f ON ac.registration = f.aircraft_registration
        GROUP BY ac.registration, ac.model
        HAVING COUNT(f.flight_id) > 5
        ORDER BY flight_count DESC;
        """
    },
    {
        "id": 3,
        "title": "3) Airports with > 5 Outbound Flights",
        "description": "For each airport, display its name and the number of outbound flights, but only for airports with more than 5 outbound flights.",
        "sql": """
        SELECT 
            ap.name AS airport_name,
            COUNT(f.flight_id) AS outbound_count
        FROM airport ap
        JOIN flights f ON ap.iata_code = f.origin_iata
        GROUP BY ap.name, ap.iata_code
        HAVING COUNT(f.flight_id) > 5
        ORDER BY outbound_count DESC;
        """
    },
    {
        "id": 4,
        "title": "4) Top 3 Destination Airports by Arrivals",
        "description": "Find the top 3 destination airports (name, city) by number of arriving flights, sorted by count descending.",
        "sql": """
        SELECT 
            ap.name AS airport_name,
            ap.city,
            COUNT(f.flight_id) AS arrival_count
        FROM airport ap
        JOIN flights f ON ap.iata_code = f.destination_iata
        GROUP BY ap.name, ap.city, ap.iata_code
        ORDER BY arrival_count DESC
        LIMIT 3;
        """
    },
    {
        "id": 5,
        "title": "5) Flight Classification (Domestic vs International)",
        "description": "Show for each flight: number, origin, destination, and a label 'Domestic' or 'International' using CASE WHEN on country match.",
        "sql": """
        SELECT 
            f.flight_number,
            f.origin_iata,
            f.destination_iata,
            orig.country AS origin_country,
            dest.country AS destination_country,
            CASE 
                WHEN orig.country = dest.country THEN 'Domestic' 
                ELSE 'International' 
            END AS flight_type
        FROM flights f
        JOIN airport orig ON f.origin_iata = orig.iata_code
        JOIN airport dest ON f.destination_iata = dest.iata_code
        ORDER BY f.flight_number;
        """
    },
    {
        "id": 6,
        "title": "6) 5 Most Recent Arrivals at DEL",
        "description": "Show the 5 most recent arrivals at 'DEL' airport including flight number, aircraft, departure airport name, and arrival time, ordered by latest arrival.",
        "sql": """
        SELECT 
            f.flight_number,
            f.aircraft_registration,
            orig.name AS departure_airport_name,
            f.actual_arrival AS arrival_time
        FROM flights f
        JOIN airport orig ON f.origin_iata = orig.iata_code
        WHERE f.destination_iata = 'DEL'
        ORDER BY f.actual_arrival DESC
        LIMIT 5;
        """
    },
    {
        "id": 7,
        "title": "7) Airports with No Arriving Flights",
        "description": "Find all airports with no arriving flights (never used as a destination in flights table).",
        "sql": """
        SELECT 
            ap.iata_code,
            ap.name,
            ap.city,
            ap.country
        FROM airport ap
        WHERE ap.iata_code NOT IN (
            SELECT DISTINCT f.destination_iata 
            FROM flights f 
            WHERE f.destination_iata IS NOT NULL
        )
        ORDER BY ap.iata_code;
        """
    },
    {
        "id": 8,
        "title": "8) Airline Flights by Status Summary",
        "description": "For each airline, count the number of flights by status (e.g., 'On Time', 'Delayed', 'Cancelled') using CASE WHEN.",
        "sql": """
        SELECT 
            f.airline_code,
            SUM(CASE WHEN f.status = 'On Time' THEN 1 ELSE 0 END) AS on_time_count,
            SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_count,
            SUM(CASE WHEN f.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
            COUNT(f.flight_id) AS total_flights
        FROM flights f
        GROUP BY f.airline_code
        ORDER BY total_flights DESC;
        """
    },
    {
        "id": 9,
        "title": "9) Cancelled Flights Details",
        "description": "Show all cancelled flights, with aircraft and both airports, ordered by departure time descending.",
        "sql": """
        SELECT 
            f.flight_number,
            f.aircraft_registration,
            orig.name AS origin_airport,
            dest.name AS destination_airport,
            f.scheduled_departure
        FROM flights f
        JOIN airport orig ON f.origin_iata = orig.iata_code
        JOIN airport dest ON f.destination_iata = dest.iata_code
        WHERE f.status = 'Cancelled'
        ORDER BY f.scheduled_departure DESC;
        """
    },
    {
        "id": 10,
        "title": "10) City Pairs with > 2 Aircraft Models",
        "description": "List all city pairs (origin-destination) that have more than 2 different aircraft models operating flights between them.",
        "sql": """
        SELECT 
            orig.city AS origin_city,
            dest.city AS destination_city,
            COUNT(DISTINCT ac.model) AS unique_models_count
        FROM flights f
        JOIN airport orig ON f.origin_iata = orig.iata_code
        JOIN airport dest ON f.destination_iata = dest.iata_code
        JOIN aircraft ac ON f.aircraft_registration = ac.registration
        GROUP BY orig.city, dest.city
        HAVING COUNT(DISTINCT ac.model) > 2
        ORDER BY unique_models_count DESC;
        """
    },
    {
        "id": 11,
        "title": "11) Delay Percentage per Destination",
        "description": "For each destination airport, compute the % of delayed flights (status='Delayed') among all arrivals, sorted by highest percentage.",
        "sql": """
        SELECT 
            dest.name AS destination_airport,
            COUNT(f.flight_id) AS total_arrivals,
            SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_arrivals,
            ROUND(
                (SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) * 100.0) / COUNT(f.flight_id), 
                2
            ) AS delay_percentage
        FROM flights f
        JOIN airport dest ON f.destination_iata = dest.iata_code
        GROUP BY dest.name, dest.iata_code
        ORDER BY delay_percentage DESC;
        """
    }
]

def run_query(query_id):
    query_obj = next((q for q in QUERIES if q["id"] == query_id), None)
    if not query_obj:
        raise ValueError(f"Query ID {query_id} not found.")
    
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_query(query_obj["sql"], conn)
    return df

def test_all_queries():
    print("Testing all queries...")
    for q in QUERIES:
        print(f"\nRunning Query {q['id']}: {q['title']}")
        try:
            df = run_query(q["id"])
            print(f"Result count: {len(df)}")
            print(df.to_string())
        except Exception as e:
            print(f"Error executing Query {q['id']}: {e}")

if __name__ == "__main__":
    test_all_queries()
