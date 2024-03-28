import streamlit as st
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import geopandas as gpd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error



def home_page():
    st.title("ZeroDown")
    page_selection = st.sidebar.selectbox("Select Page", ["Home", "Price Estimation", 'Home Comparables',"Duplicates","Visualization"])
    return page_selection

def home_comparables():
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


username ='postgres'
password = 'iamgroot!!!'
host = 'localhost'
port = '5433'
dbname = 'zd'



conn_str = f'postgresql://{username}:{password}@{host}:{port}/{dbname}'
engine = create_engine(conn_str)
st.set_option('deprecation.showPyplotGlobalUse', False)
# Function to query database and retrieve data for plots
def fetch_data(query):
    return pd.read_sql(query, engine)

# Function to plot earliest and latest listing dates
def plot_listing_dates():
    date_query = """
        SELECT MIN(listing_contract_date) AS earliest_date, MAX(listing_contract_date) AS latest_date
        FROM home_info;
    """
    date_df = fetch_data(date_query)
    date_df['earliest_date'] = pd.to_datetime(date_df['earliest_date'])
    date_df['latest_date'] = pd.to_datetime(date_df['latest_date'])

    plt.figure(figsize=(10, 6))
    plt.plot(date_df['earliest_date'], label='Earliest Date', marker='o')
    plt.plot(date_df['latest_date'], label='Latest Date', marker='o')
    plt.title('Earliest and Latest Listing Dates')
    plt.xlabel('Date')
    plt.ylabel('Listing Count')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    st.pyplot()

# Function to plot status frequency
def plot_status_frequency():
    status_query = """
        SELECT status, COUNT(*) AS frequency
        FROM home_info
        GROUP BY status;
    """
    status_df = fetch_data(status_query)

    plt.figure(figsize=(10, 6))
    plt.bar(status_df['status'], status_df['frequency'], color='skyblue')
    plt.title('Frequency of Status')
    plt.xlabel('Status')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot()

# Function to plot home type frequency
def plot_home_type_frequency():
    # Assuming you have loaded the data into home_type_df DataFrame
    # Example:
    home_type_query = """
        SELECT home_type, COUNT(*) AS frequency
        FROM home_info
        GROUP BY home_type;
    """
    home_type_df = fetch_data(home_type_query)

    
    # Drop rows with missing values
    home_type_df.dropna(inplace=True)
    
    # Plot the data
    plt.figure(figsize=(8, 6))
    plt.bar(home_type_df['home_type'], home_type_df['frequency'], color='lightgreen')
    plt.xlabel('Home Type')
    plt.ylabel('Frequency')
    plt.title('Frequency of Home Types')
    plt.xticks(rotation=45)
    st.pyplot()

def plot_listings_over_months():
    query = """
        SELECT EXTRACT(YEAR FROM listing_contract_date) AS year,
               EXTRACT(MONTH FROM listing_contract_date) AS month,
               COUNT(*) AS listings_count
        FROM home_info
        GROUP BY year, month
        ORDER BY year, month;
    """
    listings_over_months_df = fetch_data(query)
    
    # Plot the data
    plt.figure(figsize=(8, 6))
    plt.plot(listings_over_months_df['year'].astype(str) + '-' + listings_over_months_df['month'].astype(str), listings_over_months_df['listings_count'], marker='o')
    plt.xlabel('Year-Month')
    plt.ylabel('Listings Count')
    plt.title('Distribution of Listings Over Months')
    plt.xticks(rotation=45)
    st.pyplot()

# Function to plot average listing price per year
def plot_avg_listing_price_per_year():
    query = """
        SELECT EXTRACT(YEAR FROM listing_contract_date) AS year,
               AVG(listing_price) AS avg_listing_price
        FROM home_info
        GROUP BY year
        ORDER BY year;
    """
    avg_listing_price_df = fetch_data(query)
    
    # Plot the data
    plt.figure(figsize=(8, 6))
    plt.plot(avg_listing_price_df['year'], avg_listing_price_df['avg_listing_price'], marker='o')
    plt.xlabel('Year')
    plt.ylabel('Average Listing Price')
    plt.title('Average Listing Price Per Year')
    st.pyplot()

# Function to plot weekly trends
def plot_weekly_trends():
    query = """
        SELECT DATE_TRUNC('week', listing_contract_date) AS week_start,
               COUNT(*) AS listings_count
        FROM home_info
        GROUP BY week_start
        ORDER BY week_start;
    """
    weekly_trends_df = fetch_data(query)
    
    # Plot the data
    plt.figure(figsize=(8, 6))
    plt.plot(weekly_trends_df['week_start'], weekly_trends_df['listings_count'], marker='o')
    plt.xlabel('Week Start Date')
    plt.ylabel('Listings Count')
    plt.title('Weekly Trends')
    plt.xticks(rotation=45)
    st.pyplot()
def plot_outliers():

    # Execute the SQL query
    query = """
    WITH quartiles AS (
        SELECT 
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY listing_price) AS q1_price,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY listing_price) AS q3_price,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY finished_sqft) AS q1_sqft,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY finished_sqft) AS q3_sqft
        FROM home_info
    ),
    iqr AS (
        SELECT 
            q1_price,
            q3_price,
            q3_price - q1_price AS iqr_price,
            q1_sqft,
            q3_sqft,
            q3_sqft - q1_sqft AS iqr_sqft
        FROM quartiles
    )
    SELECT 
        id,
        listing_price,
        finished_sqft,
        CASE 
            WHEN listing_price < i.q1_price - 1.5 * i.iqr_price OR listing_price > i.q3_price + 1.5 * i.iqr_price THEN 'Outlier'
            ELSE 'Not Outlier'
        END AS price_outlier_status,
        CASE 
            WHEN finished_sqft < i.q1_sqft - 1.5 * i.iqr_sqft OR finished_sqft > i.q3_sqft + 1.5 * i.iqr_sqft THEN 'Outlier'
            ELSE 'Not Outlier'
        END AS sqft_outlier_status
    FROM home_info h, iqr i, quartiles q;
    """
    df = pd.read_sql(query, engine)

    # Plot the outliers
    plt.figure(figsize=(10, 6))
    plt.scatter(df['listing_price'], df['finished_sqft'], c='blue', label='Not Outlier')
    plt.scatter(df[df['price_outlier_status'] == 'Outlier']['listing_price'], 
                df[df['price_outlier_status'] == 'Outlier']['finished_sqft'], 
                c='red', label='Price Outlier')
    plt.scatter(df[df['sqft_outlier_status'] == 'Outlier']['listing_price'], 
                df[df['sqft_outlier_status'] == 'Outlier']['finished_sqft'], 
                c='green', label='Sqft Outlier')
    plt.xlabel('Listing Price')
    plt.ylabel('Finished Sqft')
    plt.title('Outliers in Listing Price vs Finished Sqft')
    plt.legend()
    plt.grid(True)
    st.pyplot()
def plot_geographical_spread():

    query = "SELECT id, geom FROM market_geom;"
    gdf = gpd.read_postgis(query, con=engine)

    gdf.plot()
    plt.title('Geographical Spread')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    st.pyplot()

# Streamlit app

def visualization():
    st.title('Real Estate Data Visualization')

    page = st.sidebar.selectbox('Select a plot', ['Earliest and Latest Listing Dates', 'Status Frequency', 'Home Type Frequency','Geographical Spread',
                                                  'Listings Over Months', 'Average Listing Price Per Year', 'Weekly Trends','Outliers'])

    if page == 'Earliest and Latest Listing Dates':
        st.header('Earliest and Latest Listing Dates')
        plot_listing_dates()
    elif page == 'Status Frequency':
        st.header('Status Frequency')
        plot_status_frequency()
    elif page == 'Home Type Frequency':
        st.header('Home Type Frequency')
        plot_home_type_frequency()
    elif page == 'Listings Over Months':
        st.header('Listings Over Months')
        plot_listings_over_months()
    elif page == 'Average Listing Price Per Year':
        st.header('Average Listing Price Per Year')
        plot_avg_listing_price_per_year()
    elif page == 'Weekly Trends':
        st.header('Weekly Trends')
        plot_weekly_trends()
    elif page == 'Outliers':
        st.header("Outliers")
        plot_outliers()
    elif page=='Geographical Spread':
        st.header("Geographical Spread")
        plot_geographical_spread()

def duplicates():
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

def priceestimation():
    
    # Function to preprocess data
    def preprocess_data(data):
        # Drop unnecessary columns
        data = data[['bedrooms', 'bathrooms', 'zipcode_market_id', 'finished_sqft', 'lot_size_sqft', 'year_built', 'listing_price']]

        # Handle missing values if any
        data.dropna(inplace=True)

        # Split features and target variable
        X = data.drop(columns=['listing_price'])
        y = data['listing_price']

        # Normalize numerical features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        return X_scaled, y

    # Train-test split
    def split_data(X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test

    # Model training
    def train_model(X_train, y_train):
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        return model

    # Model evaluation
    def evaluate_model(model, X_test, y_test):
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = mse ** 0.5
        return rmse




    # Function to fetch actual listing price from the database
    def fetch_actual_price(connection, bedrooms, bathrooms, zipcode, finished_sqft, lot_size_sqft, year_built):
        cursor = connection.cursor()
        query = """
            SELECT listing_price
            FROM home_info
            WHERE bedrooms = %s
            AND bathrooms = %s
            AND zipcode_market_id = %s
            AND finished_sqft = %s
            AND lot_size_sqft = %s
            AND year_built = %s
            LIMIT 1;
        """
        cursor.execute(query, (bedrooms, bathrooms, zipcode, finished_sqft, lot_size_sqft, year_built))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        else:
            return None

    # Title and description
    st.title("Home Listing Price Prediction")
    st.write("Enter the details of the home to predict its listing price.")

    # User inputs for home attributes
    bedrooms = st.number_input("Bedrooms", min_value=1, value=4)
    bathrooms = st.number_input("Bathrooms", min_value=1, value=4)
    zipcode = st.number_input("Zipcode", min_value=10000, value=14710)
    finished_sqft = st.number_input("Finished Sqft", min_value=1, value=3950)
    lot_size_sqft = st.number_input("Lot Size Sqft", min_value=1, value=3441)
    year_built = st.number_input("Year Built", min_value=1800, value=2009)

    conn = psycopg2.connect(database="zd", user="postgres", password="iamgroot!!!", host="localhost", port="5433")

    # Query data from PostgreSQL
    query = """
        SELECT bedrooms, bathrooms, zipcode_market_id, finished_sqft, lot_size_sqft, year_built, listing_price
        FROM home_info;
    """
    data = pd.read_sql(query, conn)

    X, y = preprocess_data(data)

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Train the model
    model = train_model(X_train, y_train)


    # Button to trigger prediction
    if st.button("Predict Listing Price"):
        # Make predictions
        
        new_data = [[bedrooms, bathrooms, zipcode, finished_sqft, lot_size_sqft, year_built]]
        predicted_price = model.predict(new_data)

        # Display predicted price
        st.subheader("Predicted Listing Price")
        st.write(f"${predicted_price[0]:.2f}")


        # Fetch actual listing price
        actual_price = fetch_actual_price(conn, bedrooms, bathrooms, zipcode, finished_sqft, lot_size_sqft, year_built)
        
        # Close the database connection
        conn.close()

        # Display actual listing price
        st.subheader("Actual Listing Price")
        if actual_price is not None:
            st.write(f"${actual_price:.2f}")
        else:
            st.write("Actual listing price not found in the database.")


def main():
    page = home_page()

    if page == "Home":
        st.write("Welcome to the Home Page!")
    elif page == "Home Comparables":
        home_comparables()
    elif page == "Visualization":
        visualization()
    elif page == "Duplicates":
        duplicates()    
    elif page == "Price Estimation":
        priceestimation()    

if __name__ == "__main__":
    main()
