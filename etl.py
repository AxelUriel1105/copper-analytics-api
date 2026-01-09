import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(DATABASE_URL)

def extract_copper_data():
    print("Descargando datos del Cobre (HG=F)...")
    # Descargar datos del último mes
    copper = yf.Ticker("HG=F")
    hist = copper.history(period="1mo") # '1mo' = 1 mes, '1y' = 1 año
    # Limpieza básica (Reset index para que la fecha sea una columna)
    hist.reset_index(inplace=True)
    # Seleccionar solo lo que nos interesa
    df_clean = hist[['Date', 'Close', 'Volume']].copy()
    # Renombrar columnas para que se vean profesionales
    df_clean.columns = ['date', 'price_close', 'volume']
    df_clean['date'] = df_clean['date'].dt.tz_localize(None)
    #print(df_clean.head())
    
    return df_clean

def load_data_to_sql(df):
    print("Conectando a Docker PostgreSQL...")
    df.to_sql('copper_prices', con=engine, index=False, if_exists='replace')
    print("Datos guardados en PostgreSQL dentro del contenedor Docker.")

def run_pipeline():
    data = extract_copper_data()
    if not data.empty:
        load_data_to_sql(data)
    else:
        print("No se encontraron datos.")
if __name__ == "__main__":
    run_pipeline()