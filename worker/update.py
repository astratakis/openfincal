import os
import logging
import psycopg2
from psycopg2.extras import execute_values
import yfinance as yf
import pandas as pd

# Configure logging for Cloud Run (which automatically captures stdout)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Establish a connection to the openfincal PostgreSQL database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "openfincal.com"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

def main():
    logging.info("Starting daily corporate event gatherer...")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        return

    # 1. Fetch Tickers
    logging.info("Fetching ticker symbols from database...")
    cur.execute("SELECT symbol FROM tickers;")
    tickers = [row[0] for row in cur.fetchall()]
    logging.info(f"Retrieved {len(tickers)} tickers.")

    events_to_insert = []

    # 2. Fetch Calendar Events via yfinance
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            cal = stock.calendar
            
            # yfinance calendar output is usually a dict. We look for 'Earnings Date'
            if isinstance(cal, dict) and 'Earnings Date' in cal:
                dates = cal['Earnings Date']
                for date_obj in dates:
                    # Convert to standard YYYY-MM-DD string
                    event_date = date_obj.strftime('%Y-%m-%d')
                    # Append tuple matching the columns in your database
                    events_to_insert.append((ticker, event_date, 'Earnings'))
                    
        except Exception as e:
            logging.warning(f"Failed to fetch calendar for {ticker}: {e}")

    # 3. Bulk Insert into Database
    if events_to_insert:
        logging.info(f"Inserting {len(events_to_insert)} events into the database...")
        
        # Using ON CONFLICT to avoid duplicate entries if the job runs twice or dates overlap
        insert_query = """
            INSERT INTO events (ticker_symbol, event_date, event_type) 
            VALUES %s 
            ON CONFLICT (ticker_symbol, event_date, event_type) DO NOTHING;
        """
        
        try:
            execute_values(cur, insert_query, events_to_insert)
            conn.commit()
            logging.info("Successfully inserted events.")
        except Exception as e:
            conn.rollback()
            logging.error(f"Database insertion failed: {e}")
    else:
        logging.info("No new events found to insert.")

    cur.close()
    conn.close()
    logging.info("Job complete. Connection closed.")

if __name__ == "__main__":
    main()
