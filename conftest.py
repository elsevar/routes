from pytest import fixture
from api import Api
from orm import Table, Column, ForeignKey, Database
import os

@fixture
def api():
    return Api()

@fixture
def client(api):
    return api.test_session()

@fixture
def db():
    DB_PATH = "./test.db"
    try:
        if os.path.exists(DB_PATH):
            db = Database(DB_PATH)
            db.conn.close()
            os.remove(DB_PATH)
    except:
        pass
    db = Database(DB_PATH)
    return db

@fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)
    
    return Author

@fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)

    return Book