import pymongo
import os

# replace with sql based solution - perhaps mariadb container? or mysqlserver?

class Database(object): 
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(os.environ.get('MONGO_URL'))
        Database.DATABASE = client.get_database("is-db")

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

