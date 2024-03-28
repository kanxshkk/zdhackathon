import streamlit as st
import psycopg2
import pandas as pd

# Function to fetch data from the database based on the selected query type
def fetch_data(query_type, cursor):
    if query_type == 'Absolute Duplicate':
        query = """
            SELECT *
            FROM home_info h1
            WHERE EXISTS (
                SELECT 1
                FROM home_info h2
                WHERE h1.address = h2.address
                  AND ABS(EXTRACT(DAY FROM h1.listing_contract_date - h2.listing_contract_date)) <= 7
            )
            ORDER BY address;
        """
    else:  # Pseudo Duplicate
        query = """
            SELECT *
            FROM home_info
            WHERE address IN (
                SELECT address
                FROM home_info
                GROUP BY address
                HAVING COUNT(DISTINCT listing_contract_date) > 1
            )
            ORDER BY address;
        """

    cursor.execute(query)
    data = cursor.fetchall()

    return data

# Streamlit UI code
def main():
    st.title('Homes Deduplication')

    # Connect to the database
    conn = psycopg2.connect(database="zd", user="postgres", password="iamgroot!!!", host="localhost", port="5433")
    cursor = conn.cursor()

    # Select query type
    query_type = st.radio("Select Query Type", ('Absolute Duplicate', 'Pseudo Duplicate'))

    # Button to fetch data
    if st.button('Fetch Data'):
        data = fetch_data(query_type, cursor)

        # Display results
        if data:
            df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
            st.write(df)
        else:
            st.write('No data found.')

    # Close the database connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
