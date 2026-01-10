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

def extract_data():
    """
    Extraer datos del cobre y del tipo de cambio USD/MXN
    """
    # Datos del cobre
    print("Descargando datos del Cobre (HG=F)...")
    # Descargar datos del último mes
    copper = yf.Ticker("HG=F").history(period="1mo")
    copper = copper[['Close', 'Volume']].reset_index()
    # Renombrar para evitar confusiones al unir
    copper.columns = ['date', 'price_usd', 'volume']
    
    # Tipo de cambio (USD a MXN)
    print("Descargando Tipo de Cambio (MXN=X)...")
    usd_mxn = yf.Ticker("MXN=X").history(period="1mo")
    usd_mxn = usd_mxn[['Close']].reset_index()
    usd_mxn.columns = ['date', 'mxn_rate']
    return copper, usd_mxn

def transform_data(copper_df, exchange_df):
    """
    Limpia, une los dataframes y calcula los precios en pesos
    """
    print("Fase de transformación")
    # Normalizar fechas (quitar hora y zona horaria para que coincidan perfectamente)
    copper_df['date'] = copper_df['date'].dt.date
    exchange_df['date'] = exchange_df['date'].dt.date
    
    # Unir las dos tablas basándonos en la fecha con merge
    # Usamos inner para quedarnos solo con días que tengan datos en ambos lados
    df_merged = pd.merge(copper_df, exchange_df, on='date', how='inner')
    
    # Crear la columna en pesos
    # El cobre cotiza en libras, así que el precio es por libra
    df_merged['price_mxn'] = df_merged['price_usd'] * df_merged['mxn_rate']
    
    # Redondear a 2 decimales
    df_merged['price_usd'] = df_merged['price_usd'].round(2)
    df_merged['mxn_rate'] = df_merged['mxn_rate'].round(2)
    df_merged['price_mxn'] = df_merged['price_mxn'].round(2)
    
    print(f"Transformación completa. Filas resultantes: {len(df_merged)}")
    print(df_merged.head()) 
    
    return df_merged

def load_data_to_sql(df):
    print('Fase de carga')
    print("Conectando a Docker PostgreSQL...")
    df.to_sql('copper_prices', con=engine, index=False, if_exists='replace')
    print("Datos guardados en PostgreSQL dentro del contenedor Docker.")

def run_pipeline():
    # 1. Extract
    copper_raw, mxn_raw = extract_data()
    # 2. Transform
    if not copper_raw.empty and not mxn_raw.empty:
        df_final = transform_data(copper_raw, mxn_raw)
        # 3. Load
        load_data_to_sql(df_final)
    else:
        print("Error: No se pudieron descargar datos.")
if __name__ == "__main__":
    run_pipeline()