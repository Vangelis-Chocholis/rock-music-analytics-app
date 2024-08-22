import pypyodbc as odbc
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import pandas as pd
from dotenv import load_dotenv
import os
import time
import streamlit as st



def set_connection_string():
    # connect to database
    # specify server and DB name
    server = "spotifyrockdb.database.windows.net"
    database = "SpotifyRockDB"

    # load credentials
    try:
        #load_dotenv()
        # get password locally
        #password = os.getenv("PASSWORD")
        # get password from GitHub secrets
        #password = os.environ["PASSWORD"]
        # get password from Streamlit secrets
        password = st.secrets["PASSWORD"]
        # set connection string
        connection_string = (
        'Driver={ODBC Driver 18 for SQL Server};'
        'Server=tcp:' + server + ',1433;'
        'Database=' + database + ';'
        'Uid=sqladmin;'
        'Pwd=' + password + ';'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=600;')
        return connection_string
        
    except Exception as e:
        print("An exception occurred: Database PASSWORD not found")
        return None
                                                                    


# connect to database using pyodbc (without SQLAlchemy)
def database_connection(connection_string, max_retries=15, retry_delay=1):
    """Connect to SQL Server using pyodbc

    Args:
        connection_string (string): The connection string to the database
        max_retries (int, optional): Max number of retries. Defaults to 15.
        retry_delay (int, optional): Number of seconds to delay between retries. Defaults to 1.

    Returns:
        odbc connection: The connection to the database
    """
    attempts = 0
    while attempts < max_retries:
        try:
            conn = odbc.connect(connection_string)
            return conn
        except Exception as e:
            #logging.error(f"An exception occurred: connect with DB failed (Attempt {attempts + 1}/{max_retries})", exc_info=False)
            attempts += 1
            time.sleep(retry_delay)
            print(f"Failed to connect to the database. Exception raised: {e}")
    return None


# set SQLAlchemy engine
def set_engine(conn, max_retries=5, retry_delay=2):
    """Creates a SQLAlchemy engine using a preexisting connection

    Args:
        conn (odbc deonnection): The connection to the database
        max_retries (int, optional): Max number of retries. Defaults to 5.
        retry_delay (int, optional): Number of seconds to delay between retries. Defaults to 2.

    Returns:
        SQLAlchemy engine: The SQLAlchemy engine
    """
    attempts = 0
    while attempts < max_retries:
        try:
            engine = create_engine("mssql+pyodbc://", poolclass=StaticPool, creator=lambda: conn)
            return engine
        except Exception as e:
            print(f"An exception occurred: SQLAlcehmy engine error (Attempt {attempts + 1}/{max_retries})")
            attempts += 1
            time.sleep(retry_delay)

    print(f"Failed to create the SQLAlchemy engine after {max_retries} attempts. Exception raised: {e}")
    try:
        conn.close()
        print("Connection closed")
    except Exception as e:
        print(f"An exception occurred: failed to close the connection. Exception raised: {e}")
    return None



def get_data_from_db(sql, engine):
    """Get data from database using a SQL query

    Args:
        sql (string): The SQL query
        engine (SQL Alchemy engine, optional): Defaults to set_engine(database_connection(connection_string)).

    Returns:
        pandas.DataFrame: The data from the database
    """
    try:
        data = pd.read_sql(sql, engine)
        engine.dispose()
        return data
    except Exception as e:
        print(f"An exception occurred: SQL query failed. Exception raised: {e}")
        engine.dispose()
        return None
    


def load_from_db(sql):
    """Load data from database using a SQL query

    Args:
        sql (string): The SQL query
    """
    # get connection string
    connection_string = set_connection_string()
    # connect to database
    conn = database_connection(connection_string)
    # set SQLAlchemy engine
    engine = set_engine(conn)
    # get data from database
    data = get_data_from_db(sql, engine)
    return data 



####### Update dynamic data
table_names = [
    'tracks_popularity_table',
    'albums_popularity_table',
    'artists_popularity_table',
    'artists_followers_table'
]

# Function to load data from CSV
def load_data_from_csv(table_name):
    return pd.read_csv(f"data/{table_name}.csv")

# Function to get the latest date from the data
def get_latest_date(data):
    return data['date'].max()

# Function to query new data from the database
def get_new_data(table_name, latest_date):
    """
    Retrieves new data from the specified table in the database.

    Args:
        table_name (str): The name of the table to retrieve data from.
        latest_date (str): The latest date to filter the data.

    Returns:
        pandas.DataFrame: A DataFrame of new data records retrieved from the database.
    """
    sql_query = f"SELECT * FROM {table_name} WHERE date > '{latest_date}';"
    new_data = load_from_db(sql_query)
    return new_data

# Function to update the CSV file with new data
def update_data(table_name, data, new_data, update_csv):
    """
    Updates the given data with new_data and optionally updates the corresponding CSV file.

    Args:
        table_name (str): The name of the table or dataset.
        data (pandas.DataFrame): The original data to be updated.
        new_data (pandas.DataFrame): The new data to be added to the original data.
        update_csv (bool, optional): Whether to update the corresponding CSV file. Defaults to False.

    Returns:
        pandas.DataFrame: The updated data.

    """
    if not new_data.empty:
        updated_data = pd.concat([data, new_data], ignore_index=True)
        if update_csv == True:
            updated_data.to_csv(f"data/{table_name}.csv", index=False)
    else:
        updated_data = data
    return updated_data


# Main function to update all tables and return the updated data
def update_dynamic_tables():
    """
    Updates all tables in the database with new data.
    
    This function iterates over a list of table names and performs the following steps for each table:
    1. Loads existing data from a CSV file.
    2. Determines the latest date in the existing data.
    3. Retrieves new data from the database that is more recent than the latest date.
    4. Updates the CSV file with the new data and stores the updated data.
    
    Returns:
        dict: A dictionary containing the updated data for each table, with table names as keys.
    """
    updated_tables = {}
    
    for table_name in table_names:
        # Load existing data from CSV
        data = load_data_from_csv(table_name)
        
        # Get the latest date in the existing data
        latest_date = get_latest_date(data)
        
        # Get new data from the database
        new_data = get_new_data(table_name, latest_date)
        
        # Update the CSV with new data and store the updated data
        updated_data = update_data(table_name, data, new_data, update_csv=False)
        updated_tables[table_name] = updated_data
        
        #print(f"Updated {table_name}.csv with {len(new_data)} new records.")
    
    return updated_tables

# Test: access the updated data
'''updated_tables = update_dynamic_tables()
tracks_popularity_table = updated_tables['tracks_popularity_table']
albums_popularity_table = updated_tables['albums_popularity_table']
artists_popularity_table = updated_tables['artists_popularity_table']
artists_followers_table = updated_tables['artists_followers_table']'''



# test code

# SQL query to get the tracks with the current popularity
sql1 = '''
  SELECT  *
    FROM tracks_table t JOIN albums_table a ON t.album_id=a.album_id
    JOIN artists_table ar ON a.artist_id = ar.artist_id
    JOIN tracks_features_table tf ON t.track_id = tf.track_id
    JOIN tracks_popularity_table tp ON t.track_id = tp.track_id
    WHERE tp.date = (SELECT MAX(date) FROM tracks_popularity_table);
'''


# test code
# track time to execute the query
sql ='''SELECT * FROM artists_followers_table;'''

'''
start = time.time()
data = load_from_db(sql)
end = time.time()
print(f"Time to execute the query: {end-start}")
print(data)
data.to_csv("data/artists_followers_table.csv", index=False)
'''







'''# test DB connection
conn_str = set_connection_string()
conn = database_connection(conn_str)
print(conn)

# test engine
engine = set_engine(conn)
print(engine)
engine.dispose()
'''
