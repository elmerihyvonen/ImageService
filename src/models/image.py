import uuid

from src.common.database import Database


class Image(object):

    def __init__(self, username: str, caption: str, filename: str, directory: str, _id=None):

        self._id = self._id = uuid.uuid4().hex if _id is None else _id
        self.username = username # Who owns the image
        self.caption = caption
        self.filename = filename
        self.directory = directory


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
            "directory": self.directory
        }

    @classmethod
    def new_image(cls, username, caption, filename, directory):

        image = Database.find_one(collection='images', query={'username': username, 'filename': filename})

        # checks if this filename already exists for this username
        if image is None:
            new_image = Image(username, caption, filename, directory)
            new_image.save_to_mongo()
            return True

        else:
            # return False if the image was already there
            return False



    @classmethod
    def image_from_mongo(cls, filename):
        image_data = Database.find_one(collection='images', query={'filename': filename})
        return cls(**image_data)


    @classmethod
    def images_from_mongo(cls, username):

        images = Database.find(collection="images",
                               query={'username': username})

        return [cls(**image) for image in images]

        # return [image for image in Database.find(collection='images', query={'owner_id': owner_id})]