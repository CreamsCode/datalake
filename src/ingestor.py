from .models import Word, WordUsage

class DataIngestor:
    def __init__(self, connection_manager):
        """
        Inicializa el DataIngestor con un administrador de conexión.
        """
        self.words_collection = connection_manager.get_or_create_collection("words")
        self.usage_collection = connection_manager.get_or_create_collection("word_usage")

    def insert_word(self, word):
        """
        Inserta una palabra en la colección `words` si no existe.
        Retorna el ID del documento.
        """
        existing_word = self.words_collection.find_one({"word": word.word})
        if existing_word:
            return existing_word["_id"]  # Si ya existe, retorna su ID
        result = self.words_collection.insert_one(word.to_dict())
        return result.inserted_id

    def insert_word_usage(self, usage):
        """
        Inserta un uso de palabra en la colección `word_usage`.
        """
        self.usage_collection.insert_one(usage.to_dict())

    def process_and_insert_words(self, processed_words):
        """
        Procesa y guarda las palabras y su uso en las colecciones MongoDB.

        Args:
            processed_words (list): Lista de palabras procesadas con su información.
        """
        for entry in processed_words:
            # Crear objeto Word
            word_obj = Word(entry["word"], entry["length"])
            # Insertar palabra única o recuperar su ID
            word_id = self.insert_word(word_obj)

            # Crear objeto WordUsage
            usage_obj = WordUsage(
                word_id=word_id,
                book=entry["book"],
                author=entry["author"],
                frequency=entry["frequency"]
            )
            # Insertar el uso de la palabra
            self.insert_word_usage(usage_obj)
