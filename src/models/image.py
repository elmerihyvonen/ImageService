import uuid
import datetime
from src.common.database import Database


class Image(object):

    def __init__(self, username: str, caption: str, filename: str, author_pic: str,
                 date=None, _id=None):

        self._id = uuid.uuid4().hex if _id is None else _id
        self.username = username
        self.caption = caption
        self.filename = filename
        self.author_pic = author_pic
        self.date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M") if date is None else date


    # saving the image in to the database
    def save_to_mongo(self):
        Database.insert(collection="images",
                        data=self.json())


    def json(self):
        return {
            "_id": self._id,
            "username": self.username,
            "caption": self.caption,
            "filename": self.filename,
            "author_pic": self.author_pic,
            "date": self.date
        }


    # saves new image to database
    @classmethod
    def new_image(cls, username, caption, filename, author_pic):

        image = Database.find_one(collection='images', query={'username': username, 'filename': filename})

        # checks if this filename already exists for this username
        if image is None:
            new_image = Image(username, caption, filename, author_pic)
            new_image.save_to_mongo()
            return True

        else:
            # return False if the image was already there
            return False


    # returns a single Image object for given filename
    @classmethod
    def image_from_mongo(cls, filename):
        image_data = Database.find_one(collection='images', query={'filename': filename})
        return cls(**image_data)



    # returns all images posted by given username
    @classmethod
    def images_from_mongo(cls, username):

        images = Database.find(collection="images",
                               query={'username': username})

        return [cls(**image) for image in images]

    # returns all images posted
    @classmethod
    def all_images(cls):

        images = Database.find(collection="images", query={})

        return [cls(**image) for image in images]


    # returns a single Image object for given _id
    @classmethod
    def get_by_id(cls, image_id):
        image_data = Database.find_one(collection='images', query={'_id': image_id})
        return cls(**image_data)

    # removes a image from database with given identifier if one exists in database
    def delete_image(self):
        Database.delete_one(collection='images', query={'_id': self._id})
