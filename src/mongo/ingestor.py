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
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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
        self.logger.debug(f"Verificando si el libro '{title}' de {author} existe en la colección 'books'.")
        exists = self.books_collection.find_one({"title": title, "author": author}) is not None
        self.logger.info(f"Resultado de verificación para el libro '{title}' de {author}: {exists}")
        return exists

    def insert_book_collection(self, title, author):
        """
        Inserta un libro en la colección `books`.

        Args:
            title (str): Título del libro.
            author (str): Autor del libro.
        """
        try:
            self.books_collection.insert_one({"title": title, "author": author})
            self.logger.info(f"El libro '{title}' de {author} ha sido añadido a la colección 'books'.")
        except Exception as e:
            self.logger.error(f"Error al insertar el libro '{title}' de {author}: {e}")

    def insert_word(self, word):
        """
        Inserta una palabra en la colección `words` si no existe.
        Retorna el ID del documento.
        """
        try:
            self.logger.debug(f"Intentando insertar la palabra '{word.word}' en la colección 'words'.")
            existing_word = self.words_collection.find_one({"word": word.word})
            if existing_word:
                self.logger.info(f"La palabra '{word.word}' ya existe en la colección 'words'.")
                return existing_word["_id"]  # Si ya existe, retorna su ID
            result = self.words_collection.insert_one(word.to_dict())
            self.logger.info(f"Palabra '{word.word}' insertada correctamente con ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            self.logger.error(f"Error al insertar la palabra '{word.word}': {e}")
            return None

    def insert_word_usage(self, usage):
        """
        Inserta un uso de palabra en la colección `word_usage`.
        """
        try:
            self.logger.debug(f"Intentando insertar uso de palabra: {usage.to_dict()}")
            self.usage_collection.insert_one(usage.to_dict())
            self.logger.info(f"Uso de palabra insertado correctamente: {usage.to_dict()}")
        except Exception as e:
            self.logger.error(f"Error al insertar el uso de palabra: {e}")

    def process_and_insert_words(self, book_data):
        """
        Procesa y guarda las palabras y su uso en las colecciones MongoDB.

        Args:
            book_data (dict): Estructura con datos del libro y sus palabras.
        """
        title = book_data["book"]
        author = book_data["author"]
        words = book_data["words"]

        self.logger.info(f"Iniciando procesamiento del libro '{title}' de {author} con {len(words)} palabras.")

        # Comprobar si el libro ya existe
        if self.book_exists(title, author):
            self.logger.info(
                f"El libro '{title}' de {author} ya existe en la base de datos. Se omite el procesamiento.")
            return  # Salir si el libro ya está procesado

        # Insertar el libro como nuevo
        self.insert_book_collection(title, author)

        # Procesar e insertar las palabras y sus usos
        for index, entry in enumerate(words):
            try:
                self.logger.debug(f"Procesando palabra {index + 1}/{len(words)}: {entry}")
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
            except Exception as e:
                self.logger.error(f"Error procesando palabra: {entry}. Detalles: {e}")

        self.logger.info(f"Libro '{title}' de {author} procesado e insertado con éxito en las colecciones.")
