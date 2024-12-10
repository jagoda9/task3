import unittest

from project import app, db, books
from project.books.models import Book


class TestBook(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def testValidData(self):
        validData = [
            ("Alicja w Krainie Czarów", "Lewis Carroll",  1865, "Bajka"),
            ("Hobbit, czyli tam i z powrotem", "J.R.R. Tolkien", 1960, "Fantasy"),
            ("Gra o tron", "George R.R. Martin", 1998, "Fantasy"),
            ("I nie było już nikogo ", "Agatha Christie", 1939, "Kryminał"),
            ("Złodziej Pioruna ", "Rick Riordan", 2009, "Literatura młodzieżowa"),
        ]
        for name, author, year, type in validData:
            with app.app_context():
                book = Book(name=name, author=author, year_published=year, book_type=type)
                db.session.add(book)
                db.session.commit()
                retrieved_book = Book.query.filter_by(name=name).first()
                self.assertEqual(retrieved_book.name, name)
                self.assertEqual(retrieved_book.author, author)
                self.assertEqual(retrieved_book.year_published, year)
                self.assertEqual(retrieved_book.book_type, type)

    def testInvalidDataSign(self):
        invalidData = [
            ("Hobbit, czyli tam i z powrotem", "123", 1960, "Fantasy"),
            ("Gra o tron", "#%Jwffwf*", 1998, "Fantasy"),
            ("I nie było już nikogo ", "Agatha Christie", 1939, "*&^"),
            ("Złodziej Pioruna ", "Rick Riordan", "%^&*", "Literatura młodzieżowa"),
        ]

        for name, author, year, type in invalidData:
            with app.app_context():
                book = Book(name=name, author=author, year_published=year, book_type=type)
                with self.assertRaises(Exception):
                    db.session.add(book)
                    db.session.commit()

    def testInvalidDataYear(self):
        invalidData = [
            ("Hobbit, czyli tam i z powrotem", "J.R.R. Tolkien", 0, "Fantasy"),
            ("Gra o tron", "George R.R. Martin", -1998, "Fantasy"),
            ("I nie było już nikogo ", "Agatha Christie", 3000, "Kryminał"),
        ]
        with app.app_context():
            for name, author, year, type in invalidData:
                book = Book(name=name, author=author, year_published=year, book_type=type)
                with self.assertRaises(Exception):
                    db.session.add(book)
                    db.session.commit()

    def testMissingData(self):
        invalid_data = [
            (None, "Author", 1111, "Type"),
            ("Name", None, 1111, "Type"),
            ("Name", "Author", None, "Type"),
            ("Name", "Author", 1111, None),
        ]
        for name, author, year, type in invalid_data:
            with app.app_context():
                book = Book(name=name, author=author, year_published=year, book_type=type)
                with self.assertRaises(Exception):
                    db.session.add(book)
                    db.session.commit()

    def testXssData(self):
        invalid_data = [
            ("<script>alert('To podatność xss')</script>", "Author", 1111, "Type"),
            ("Name", "<script>alert('To podatność xss')</script>", 1111, "Type"),
            ("Name", "Author", "<script>alert('To podatność xss')</script>", "Type"),
            ("Name", "Author", 1111, "<script>alert('To podatność xss')</script>"),
        ]
        for name, author, year, type in invalid_data:
            with app.app_context():
                book = Book(name=name, author=author, year_published=year, book_type=type)
                with self.assertRaises(Exception):
                    db.session.add(book)
                    db.session.commit()

    def testSQLInjectionData(self):
        invalid_data = [
            ("\" OR 1 = 1 -- -", "Author", 1111, "Type"),
            ("Name", "\" OR 1 = 1 -- -", 1111, "Type"),
            ("Name", "Author", "\" OR 1 = 1 -- -", "Type"),
            ("Name", "Author", 1111, "\" OR 1 = 1 -- -"),
        ]
        for name, author, year, type in invalid_data:
            with app.app_context():
                book = Book(name=name, author=author, year_published=year, book_type=type)
                with self.assertRaises(Exception):
                    db.session.add(book)
                    db.session.commit()

    def testLengthData(self):
        invalid_data = [
            ("x"*65, "Author", 1911, "Type"),
            ("Name", "x"*65, 1911, "Type"),
            ("Name", "Author", 1911, "x"*21),
        ]
        for name, author, year, type in invalid_data:
            with app.app_context():
                book = Book(name=name, author=author, year_published=year, book_type=type)
                with self.assertRaises(Exception):
                    db.session.add(book)
                    db.session.commit()

    def testExtremeLengthData(self):
        invalid_data = [
            ("x"*10000000, "Author", 1911, "Type"),
            ("Name", "x"*10000000, 1911, "Type"),
            ("Name", "Author", 1911, "x"*10000000),
        ]
        for name, author, year, type in invalid_data:
            with app.app_context():
                book = Book(name=name, author=author, year_published=year, book_type=type)
                with self.assertRaises(Exception):
                    db.session.add(book)
                    db.session.commit()









if __name__ == '__main__':
    unittest.main()