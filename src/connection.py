from pymongo import MongoClient

class MongoDBConnectionManager:
    def __init__(self, uri: str = "mongodb://localhost:27017/", db_name: str = "word_analysis"):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        """
        Establece la conexión con MongoDB y selecciona la base de datos.
        """
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        print(f"Connected to MongoDB at {self.uri}")

    def get_or_create_collection(self, collection_name: str):
        """
        Verifica si una colección existe; si no, la crea y la retorna.
        """
        if self.db is None:  # Compara explícitamente con None
            raise Exception("Database connection not initialized. Call connect() first.")

        # Verificar si la colección existe
        if collection_name not in self.db.list_collection_names():
            print(f"Collection '{collection_name}' does not exist. Creating it...")
            self.db.create_collection(collection_name)  # Crea la colección si no existe

        return self.db[collection_name]

    def close(self):
        """
        Cierra la conexión con MongoDB.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")
