import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import psycopg2

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

def main():
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

if __name__ == "__main__":
    main()
