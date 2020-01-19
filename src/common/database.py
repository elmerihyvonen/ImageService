import pymongo
import os


class Database(object):
    URI = os.environ.get("MONGOLAB_URI")   # default address and port for the database
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['imageservice']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update_one(collection, query, update):
        return Database.DATABASE[collection].update_one(query, update)

    @staticmethod
    def update_many(collection, query, update):
        return Database.DATABASE[collection].update_many(query, update)

    @staticmethod
    def delete(collection, query):
        Database.DATABASE[collection].remove(query)

