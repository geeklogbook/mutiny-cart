from pymongo import MongoClient
import pandas as pd
from datetime import datetime

def get_mongo_client():
    """Retorna una conexión a MongoDB"""
    return MongoClient("mongodb://admin:password@localhost:27017/")

def get_database():
    """Retorna la base de datos mutiny"""
    client = get_mongo_client()
    return client["mutiny"]

def convert_to_dataframe(cursor):
    """Convierte un cursor de MongoDB a un DataFrame de pandas"""
    return pd.DataFrame(list(cursor))

def save_to_csv(df, filename):
    """Guarda un DataFrame en un archivo CSV"""
    df.to_csv(f"results/{filename}", index=False)
    print(f"Resultados guardados en results/{filename}")

def format_date(date_str):
    """Formatea una fecha de string a datetime"""
    if isinstance(date_str, str):
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return date_str 