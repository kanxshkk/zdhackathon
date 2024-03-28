import streamlit as st
import psycopg2

# Function to fetch similar homes from the database
def get_similar_homes(home_id, bed, bath, city_zipcode):
    conn = psycopg2.connect(database="zd", user="postgres", password="iamgroot!!!", host="localhost", port="5433")
    cursor = conn.cursor()

    # Execute a SQL query to retrieve similar homes based on the provided parameters
    query = """
        SELECT id, address
        FROM home_info
        WHERE id != %s
        AND bedrooms = %s
        AND bathrooms = %s
        AND city_market_id = %s
        LIMIT 10
    """
    cursor.execute(query, (home_id, bed, bath, city_zipcode))

    similar_homes = cursor.fetchall()  # Fetch all rows returned by the query

    conn.close()  # Close the database connection

    return similar_homes

# Function to fetch further data about the selected home
def get_home_data(home_id):
    conn = psycopg2.connect(database="zd", user="postgres", password="iamgroot!!!", host="localhost", port="5433")
    cursor = conn.cursor()

    # Execute a SQL query to retrieve data about the selected home
    query = """
        SELECT *
        FROM home_info
        WHERE id = %s
    """
    cursor.execute(query, (home_id,))
    
    home_data = cursor.fetchone()  # Fetch the row returned by the query

    conn.close()  # Close the database connection

    return home_data

# Streamlit UI code
def main():
    st.title('Home Comparables')

    # Input fields
    home_id = st.number_input('Home ID', value=39879902)
    bed = st.number_input('Number of Bedrooms', value=3)
    bath = st.number_input('Number of Bathrooms', value=2)
    city_zipcode = st.text_input('City or Zipcode', value=9686)

    # Button to fetch similar homes
    if st.button('Find Similar Homes'):
        similar_homes = get_similar_homes(home_id, bed, bath, city_zipcode)
        
        # Display the results
        st.write('Similar Homes:')
        for home in similar_homes:
            home_id, address = home
            with st.expander(address):
                home_data = get_home_data(home_id)
                attributes = [
                    "ID", "Listing Key", "Source System", "Address", "USPS Address", "Status",
                    "Listing Contract Date", "On Market Date", "Pending Date", "Last Sold Date",
                    "Off Market Date", "Original Listing Price", "Listing Price", "Last Sold Price",
                    "Home Type", "Finished Sqft", "Lot Size Sqft", "Bedrooms", "Bathrooms",
                    "Year Built", "New Construction", "Has Pool", "State Market ID", "City Market ID",
                    "Zipcode Market ID", "Neighborhood Level 1 Market ID", "Neighborhood Level 2 Market ID",
                    "Neighborhood Level 3 Market ID", "Longitude", "Latitude", "Crawler"
                ]
                for i, attribute in enumerate(home_data):  
                    st.write(f"{attributes[i]}: {attribute}")
                

if __name__ == "__main__":
    main()
