# etl.py
import yfinance as yf
import pandas as pd

def extract_copper_data():
    print("Descargando datos del Cobre (HG=F)...")
    # Descargar datos del último mes
    copper = yf.Ticker("HG=F")
    hist = copper.history(period="1mo") # '1mo' = 1 mes, '1y' = 1 año
    # Limpieza básica (Reset index para que la fecha sea una columna)
    hist.reset_index(inplace=True)
    # Seleccionar solo lo que nos interesa
    df_clean = hist[['Date', 'Close', 'Volume']]
    # Renombrar columnas para que se vean profesionales
    df_clean.columns = ['date', 'price_close', 'volume']
    
    print("Datos extraídos con éxito:")
    print(df_clean.head())
    
    return df_clean

if __name__ == "__main__":
    extract_copper_data()