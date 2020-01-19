import pymongo


class Database(object):
    URI = "mongodb://127.0.0.1:27017" #default address and port for the database
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
    def delete_one(collection, query):
        Database.DATABASE[collection].remove(query)