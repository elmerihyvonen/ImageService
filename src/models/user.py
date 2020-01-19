import uuid
from flask import session
from src.common.database import Database
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, username: str, password: str, profile_image=None, _id=None):
        self.username = username
        self.password = password
        self.profile_image = 'Anonyymi.jpeg' if profile_image is None else profile_image
        self._id = uuid.uuid4().hex if _id is None else _id


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    # this is only for internal use because it contains the password
    def json(self):

         return {
            "username": self.username,
            "password": self.password,
            "profile_image": self.profile_image,
            "_id": self._id
         }

    # method for updating profile information
    def update_profile(self, new_username, old_username, new_profile_image):

        self.username = new_username
        self.profile_image = new_profile_image

        Database.update_one(collection="users", query={"_id": self._id},
                            update={"$set": {"username": self.username,
                                             "profile_image": self.profile_image}})

        Database.update_many(collection="images", query={"username": old_username},
                            update={"$set": {"username": new_username,
                                             "author_pic": new_profile_image}})



    # method for saving users to database
    def save_to_mongo(self):
        Database.insert(collection="users", data=self.json())



    # check if the given credentials are valid
    @staticmethod
    def login_valid(username, password, bcrypt):

        user = User.get_by_username(username)

        # if there was a User with given 'username'
        # we return true if passwords match
        if user is not None:
            return bcrypt.check_password_hash(user.password, password)

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

            return True

        else:
            # user already exists
            return False


    # get User object from mongo by _id
    @classmethod
    def get_by_id(cls, user_id):

        data = Database.find_one(collection="users", query={"_id": user_id})

        # if there was a match in database with given 'username',
        # we return the matching User object
        if data is not None:
            return cls(**data)

        # if match was not found we will return None
        return None


