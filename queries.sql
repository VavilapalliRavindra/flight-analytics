-- 1) Total flights per aircraft model
SELECT 
    ac.model, 
    COUNT(f.flight_id) AS flight_count
FROM flights f
JOIN aircraft ac ON f.aircraft_registration = ac.registration
GROUP BY ac.model
ORDER BY flight_count DESC;

-- 2) Aircraft with more than 5 flights
SELECT 
    ac.registration, 
    ac.model,
    COUNT(f.flight_id) AS flight_count
FROM aircraft ac
JOIN flights f ON ac.registration = f.aircraft_registration
GROUP BY ac.registration, ac.model
HAVING COUNT(f.flight_id) > 5
ORDER BY flight_count DESC;

-- 3) Airports with more than 5 outbound flights
SELECT 
    ap.name AS airport_name,
    COUNT(f.flight_id) AS outbound_count
FROM airport ap
JOIN flights f ON ap.iata_code = f.origin_iata
GROUP BY ap.name, ap.iata_code
HAVING COUNT(f.flight_id) > 5
ORDER BY outbound_count DESC;

-- 4) Top 3 destination airports by arrived flights
SELECT 
    ap.name AS airport_name,
    ap.city,
    COUNT(f.flight_id) AS arrival_count
FROM airport ap
JOIN flights f ON ap.iata_code = f.destination_iata
GROUP BY ap.name, ap.city, ap.iata_code
ORDER BY arrival_count DESC
LIMIT 3;

-- 5) Domestic vs International flights
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

-- 6) Five most recent arrivals at Delhi (DEL)
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

-- 7) Airports with zero arriving flights
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

-- 8) Count flights by status for each airline
SELECT 
    f.airline_code,
    SUM(CASE WHEN f.status = 'On Time' THEN 1 ELSE 0 END) AS on_time_count,
    SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_count,
    SUM(CASE WHEN f.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
    COUNT(f.flight_id) AS total_flights
FROM flights f
GROUP BY f.airline_code
ORDER BY total_flights DESC;

-- 9) All cancelled flights
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

-- 10) City pairs served by more than 2 distinct aircraft models
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

-- 11) Flight delay rate by destination airport
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
