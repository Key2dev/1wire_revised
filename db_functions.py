import sqlite3
import csv

def export_to_csv(database_name:str, table_name:str, output_name:str):
    # Convert database to CSV format.
    
    # Connect to the database
    conn = sqlite3.connect(database_name)  # Replace with your database file name
    cursor = conn.cursor()

    # Query to fetch all data from the table
    query = f"SELECT * FROM {table_name}"  # Replace with your table name
    cursor.execute(query)

    # Fetch column names
    column_names = [description[0] for description in cursor.description]

    # Open a CSV file to write data
    with open(output_name, "w", newline="") as csv_file:  # Replace with desired CSV file name
        csv_writer = csv.writer(csv_file)

        # Write the column names as the first row
        csv_writer.writerow(column_names)

        # Write all rows from the database table
        csv_writer.writerows(cursor.fetchall())

    # Close the database connection
    conn.close()

    print("Export complete!")

def insert_data_to_db(database_name:str, table_name:str, date: str, t1: float, t2: float, t3: float):
    # Connect to the database and insert data (avoids accidental UI variable polluting the DB)
    conn = sqlite3.connect(database_name)
    query = f"""
    INSERT INTO {table_name} (data, t1, t2, t3)
    VALUES (?, ?, ?, ?)
    """
    cursor = conn.cursor()
    cursor.execute(query, (date, t1, t2, t3))
    conn.commit()
    conn.close()
    print(f"Data inserted into the database: {date, t1, t2, t3}")
    
def fetch_last_n_records(database, table_name, n):
    # Fetch the last n records from the database table order by id.
    # Return as list of tuples ('data' as "YYYY-MM-DD HH:MM:SS", 't1', 't2', 't3', comment)
    # TODO: This is not used in the application
    
    conn = sqlite3.connect(database)
    query = f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT {n}"
    cursor = conn.cursor()
    cursor.execute(query)
    records = cursor.fetchall()
    
    return records
    

def records_by_time_csv(database_name, table_name, start_date, end_date, output_name):
    try:
        # Connect to the database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()

        # Query to fetch data between the specified dates
        query = f"""
        SELECT data, T1, T2, T3, comment 
        FROM {table_name} 
        WHERE data BETWEEN ? AND ?
        ORDER BY data;
        """
        cursor.execute(query, (start_date, end_date))

        # Fetch column names and rows
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # Open a CSV file to write data
        with open(output_name, "w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the column names as the header
            csv_writer.writerow(column_names)

            # Write sanitized rows to the CSV
            csv_writer.writerows(rows)

        # Close the database connection
        conn.close()

        print("Export complete!")
    except Exception as e:
        print(f"An error occurred: {e}")

def fetch_filtered_data(database_name, table_name, start_date, end_date):
    try:
        # Connect to the database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()

        # Query to fetch data between the specified dates
        query = f"""
        SELECT id, data, T1, T2, T3, comment 
        FROM {table_name} 
        WHERE data BETWEEN ? AND ?
        ORDER BY data;
        """
        cursor.execute(query, (start_date, end_date))

        # Fetch column names and rows
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        return rows
    
    except Exception as e:
        print(f"An error occurred: {e}")
        rows = []
        
def add_comment(database_name, table_name, timestamp:str, comment:str):
    try:
        if len(comment)>250:
            print("Comment is too long. Maximum length is 250 characters.")
            return
        
        # Connect to the database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        # Update the comment in the database
        query = f"UPDATE {table_name} SET comment = ? WHERE data = ?"
        cursor.execute(query, (comment, timestamp))
        conn.commit()
        print("Comment updated successfully.")
        conn.close()
        
    except Exception as e:
        print(f"An error occurred while updating comment: {e}")