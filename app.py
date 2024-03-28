import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import geopandas as gpd

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
def main():
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

if __name__ == '__main__':
    main()
