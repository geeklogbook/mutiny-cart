import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGO_URI = "mongodb://admin:password@localhost:27017/"
DB_NAME = "mutiny"

# Mapeo de archivos a colecciones
FILE_COLLECTION_MAP = {
    "users.json": "users",
    "channels.json": "channels",
    "messages.json": "messages",
    "posts.json": "posts",
    "games.json": "games",
    "games_session.json": "games_sessions",
    "activity_logs.json": "activity_logs"
}

def convert_mongo_types(doc):
    """Convierte los tipos especiales de MongoDB en el formato correcto"""
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, dict):
                if "$oid" in value:
                    doc[key] = value["$oid"]
                elif "$date" in value:
                    doc[key] = value["$date"]
            else:
                doc[key] = convert_mongo_types(value)
    elif isinstance(doc, list):
        doc = [convert_mongo_types(item) for item in doc]
    return doc

def import_data():
    try:
        # Conectar a MongoDB
        client = MongoClient(MONGO_URI)
        
        # Verificar conexión
        client.admin.command('ping')
        print("Conexión a MongoDB establecida correctamente")
        
        # Obtener lista de bases de datos
        db_list = client.list_database_names()
        print(f"Bases de datos existentes: {db_list}")
        
        # La base de datos se creará automáticamente al insertar el primer documento
        db = client[DB_NAME]
        print(f"Usando base de datos: {DB_NAME}")
        
        # Directorio de datos
        data_dir = "data"
        
        # Importar cada archivo
        for filename, collection_name in FILE_COLLECTION_MAP.items():
            file_path = os.path.join(data_dir, filename)
            
            if not os.path.exists(file_path):
                print(f"Archivo no encontrado: {file_path}")
                continue
                
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            # Convertir tipos especiales de MongoDB
            data = convert_mongo_types(data)
            
            # Obtener la colección
            collection = db[collection_name]
            
            # Limpiar la colección existente
            collection.delete_many({})
            
            # Insertar los documentos
            if isinstance(data, list):
                collection.insert_many(data)
            else:
                collection.insert_one(data)
                
            print(f"Importados {len(data) if isinstance(data, list) else 1} documentos en {collection_name}")
            
        # Verificar que la base de datos se haya creado
        db_list = client.list_database_names()
        if DB_NAME in db_list:
            print(f"\nBase de datos '{DB_NAME}' creada exitosamente!")
            print(f"Colecciones en {DB_NAME}: {db.list_collection_names()}")
        else:
            print(f"\nError: La base de datos '{DB_NAME}' no se creó correctamente")
            
        print("\nImportación completada exitosamente!")
        
    except Exception as e:
        print(f"Error durante la importación: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    import_data() 