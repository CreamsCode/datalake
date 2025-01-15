class Word:
    def __init__(self, word, length):
        self.word = word
        self.length = length

    def to_dict(self):
        return {
            "word": self.word,
            "length": self.length
        }

class WordUsage:
    def __init__(self, word_id, book, author, frequency):
        self.word_id = word_id
        self.book = book
        self.author = author
        self.frequency = frequency

    def to_dict(self):
        return {
            "word_id": self.word_id,
            "book": self.book,
            "author": self.author,
            "frequency": self.frequency
        }
