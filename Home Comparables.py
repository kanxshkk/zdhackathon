from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define the database model
Base = declarative_base()

class Home(Base):
    __tablename__ = 'home_info'

    id = Column(Integer, primary_key=True)
    address = Column(String)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    finished_sqft = Column(Integer)
    listing_price = Column(Float)
    # Add more columns as needed

def connect_to_database():
    try:
        # Create a database engine
        engine = create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
            os.getenv("DB_USERNAME"),
            os.getenv("DB_PASSWORD"),
            "localhost",
            "5433",
            "zd"
        ))
        
        # Create the tables if they do not exist
        Base.metadata.create_all(engine)
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        return session
    except Exception as e:
        print("Error while connecting to PostgreSQL:", e)
        return None

def get_similar_homes(home_id, session):
    try:
        # Get the details of the given home
        home = session.query(Home).filter_by(id=home_id).first()
        if not home:
            print("No home found with the given ID.")
            return []

        # Define the criteria for similar homes (you can adjust this as needed)
        criteria = {
            "bedrooms": home.bedrooms,
            "bathrooms": home.bathrooms,
            "finished_sqft": home.finished_sqft,
            # Add more criteria here
        }

        # Query for similar homes based on the criteria
        similar_homes = session.query(Home).filter_by(**criteria).all()
        
        return similar_homes
    except Exception as e:
        print("Error while getting similar homes:", e)
        return []

def main():
    # Connect to the database
    session = connect_to_database()
    if not session:
        return
    
    # Example usage: Get similar homes for a given home ID
    home_id = 123  # Replace with the desired home ID
    similar_homes = get_similar_homes(home_id, session)
    if similar_homes:
        print("Similar homes:")
        for home in similar_homes:
            print(f"Home ID: {home.id}, Address: {home.address}")
    else:
        print("No similar homes found.")

if __name__ == "__main__":
    main()
