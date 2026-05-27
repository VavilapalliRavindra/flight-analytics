import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Airport(Base):
    __tablename__ = 'airport'
    airport_id = Column(Integer, primary_key=True, autoincrement=True)
    icao_code = Column(String(10), unique=True, nullable=False)
    iata_code = Column(String(10), unique=True, nullable=False)
    name = Column(String(255))
    city = Column(String(100))
    country = Column(String(100))
    continent = Column(String(50))
    latitude = Column(Float)                                                       
    longitude = Column(Float)
    timezone = Column(String(100))

class Aircraft(Base):
    __tablename__ = 'aircraft'
    aircraft_id = Column(Integer, primary_key=True, autoincrement=True)
    registration = Column(String(50), unique=True, nullable=False)
    model = Column(String(100))
    manufacturer = Column(String(100))
    icao_type_code = Column(String(10))
    owner = Column(String(255))

class Flight(Base):
    __tablename__ = 'flights'
    flight_id = Column(String(100), primary_key=True)
    flight_number = Column(String(50))
    aircraft_registration = Column(String(50))
    origin_iata = Column(String(10))
    destination_iata = Column(String(10))
    scheduled_departure = Column(String(100))
    scheduled_arrival = Column(String(100))
    actual_departure = Column(String(100))
    actual_arrival = Column(String(100))
    status = Column(String(50))
    airline_code = Column(String(10))

class AirportDelay(Base):
    __tablename__ = 'airport_delays'
    delay_id = Column(Integer, primary_key=True, autoincrement=True)
    airport_iata = Column(String(10))
    delay_date = Column(String(100))
    total_flights = Column(Integer)
    delayed_flights = Column(Integer)
    avg_delay_min = Column(Integer)
    median_delay_min = Column(Integer)
    canceled_flights = Column(Integer)

def get_db_url():
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    if db_type == "sqlite":
        sqlite_path = os.getenv("SQLITE_PATH", "flights.db")
        return f"sqlite:///{sqlite_path}"
    elif db_type == "postgresql":
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "flight_analytics")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "secret")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    elif db_type == "mysql":
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        name = os.getenv("DB_NAME", "flight_analytics")
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{name}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def get_engine():
    url = get_db_url()
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)

def init_db():
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    if db_type == "postgresql":
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "flight_analytics")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "secret")

        import psycopg2
        conn = None
        try:
            conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname="postgres")
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (name,))
                if not cur.fetchone():
                    cur.execute(f'CREATE DATABASE "{name}"')
                    print(f"Database '{name}' created successfully.")
        except Exception as e:
            print(f"Warning during auto-database creation: {e}")
        finally:
            if conn:
                conn.close()
    elif db_type == "mysql":
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        name = os.getenv("DB_NAME", "flight_analytics")
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")

        import mysql.connector
        conn = None
        try:
            conn = mysql.connector.connect(host=host, port=port, user=user, password=password)
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{name}`")
                print(f"Database '{name}' checked/created successfully.")
        except Exception as e:
            print(f"Warning during auto-database creation: {e}")
        finally:
            if conn:
                conn.close()

    engine = get_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

