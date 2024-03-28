import geopandas as gpd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = 'localhost'
port = '5433'
dbname = 'zd'

conn_str = f'postgresql://{username}:{password}@{host}:{port}/{dbname}'

query = "SELECT id, geom FROM market_geom;"

engine = create_engine(conn_str)

gdf = gpd.read_postgis(query, con=engine)

gdf.plot()
plt.title('Geographical Spread')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()
