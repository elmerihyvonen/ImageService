import uuid

from flask import session

from src.common.database import Database


class User(object):

    def __init__(self, username: str, password: str, _id=None):
        self.username = username
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    # this is only for internal use because it contains the password
    def json(self):

         return {
            "username": self.username,
            "password": self.password,
            "_id": self._id
         }


    # method for saving users to database
    def save_to_mongo(self):
        Database.insert(collection="users", data=self.json())



    # check if the given credentials are valid
    @staticmethod
    def login_valid(username, password):

        user = User.get_by_username(username)

        # if there was a User with given 'username'
        # we return true if passwords match
        if user is not None:
            return user.password == password

        # User was not in the database so login can not be valid
        return False


    # get User object from mongo by username identifier
    @classmethod
    def get_by_username(cls, username):

        data = Database.find_one(collection="users", query={"username": username})

        # if there was a match in database with given 'username',
        # we return the matching User object
        if data is not None:
            return cls(**data)

        # if match was not found we will return None
        return None


    # login of existing user
    @staticmethod
    def login(username):

        # login_valid has already been called
        # so we are just storing username in the session
        session['username'] = username



    # registration of new user
    # return True/False depending on
    # was there a user already
    @classmethod
    def register(cls, username, password):

        user = cls.get_by_username(username)

        # if there was not a user with given username already,
        # we can create a new one
        if user is None:

            new_user = cls(username, password)
            new_user.save_to_mongo()

            # now we can update the session as well
            session['username'] = username
            return True

        else:
            # user already exists
            return False





