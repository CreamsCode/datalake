import logging
from src.mongo.models import Word, WordUsage


class DataIngestor:
    def __init__(self, connection_manager):
        """
        Inicializa el DataIngestor con un administrador de conexión.
        """
        self.words_collection = connection_manager.get_or_create_collection("words")
        self.usage_collection = connection_manager.get_or_create_collection("word_usage")
        self.books_collection = connection_manager.get_or_create_collection("books")

        # Configuración del logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def book_exists(self, title, author):
        """
        Verifica si un libro ya existe en la colección `books`.

        Args:
            title (str): Título del libro.
            author (str): Autor del libro.

        Returns:
            bool: Verdadero si el libro existe, falso si no.
        """
        return self.books_collection.find_one({"title": title, "author": author}) is not None

    def insert_book_collection(self, title, author):
        """
        Inserta un libro en la colección `books`.

        Args:
            title (str): Título del libro.
            author (str): Autor del libro.
        """
        self.books_collection.insert_one({"title": title, "author": author})
        self.logger.info(f"El libro '{title}' de {author} ha sido añadido a la colección 'books'.")

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

    def process_and_insert_words(self, book_data):
        """
        Procesa y guarda las palabras y su uso en las colecciones MongoDB.

        Args:
            book_data (dict): Estructura con datos del libro y sus palabras.
        """
        title = book_data["book"]
        author = book_data["author"]
        words = book_data["words"]

        # Comprobar si el libro ya existe
        if self.book_exists(title, author):
            self.logger.info(
                f"El libro '{title}' de {author} ya existe en la base de datos. Se omite el procesamiento.")
            return  # Salir si el libro ya está procesado

        # Insertar el libro como nuevo
        self.insert_book_collection(title, author)

        # Procesar e insertar las palabras y sus usos
        for entry in words:
            # Crear objeto Word
            word_obj = Word(entry["word"], entry["length"])
            # Insertar palabra única o recuperar su ID
            word_id = self.insert_word(word_obj)

            # Crear objeto WordUsage
            usage_obj = WordUsage(
                word_id=word_id,
                book=title,
                author=author,
                frequency=entry["frequency"]
            )
            # Insertar el uso de la palabra
            self.insert_word_usage(usage_obj)

        self.logger.info(f"Libro '{title}' de {author} procesado e insertado con éxito en las colecciones.")
