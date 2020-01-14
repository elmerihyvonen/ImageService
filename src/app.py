from flask import Flask, request, url_for, render_template, session, send_from_directory, send_file
import os
from src.common.database import Database
from src.models.image import Image
from src.models.user import User
from src.forms import RegistrationForm, LoginForm

__author__ = "Elmeri Hyvönen"


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a3cac62b7421cb1dcd4208f9e6c51937'

# 'src/'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# before anything we need to initialize the database first
@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/')
def home():
    return render_template("/home.html")


@app.route('/login')
def login():
    form = RegistrationForm
    return render_template('login.html', msg="")


@app.route('/register')
def register():
    form = RegistrationForm()

    return render_template('register.html', msg="")


@app.route('/logout')
def logout():
    session.clear()
    return render_template("logged_out.html")


# allows only POST requests
@app.route('/auth/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    # checks if the login is valid
    if User.login_valid(username, password):
        User.login(username)

    # if login was not valid session['email'] should be None
    else:
        session['email'] = None
        return render_template('login.html', msg="Check your credentials.")

    return render_template("signedinbase.html", username=session['username'])


# again allows only POST requests
@app.route('/auth/register', methods=['POST'])
def register_user():

    username = request.form['username']
    password = request.form['password']

    # if return value is False then the 'username' is already in use
    if User.register(username, password):
        return render_template("profile.html", username=session['username'])

    else:
        return render_template('register.html', msg="Username is already in use.")

# ----------------------------------------------------------------------

@app.route('/upload', methods=['GET', 'POST'])
def upload_images():

    # lets first verify that user has logged in
    if session['username'] is not None:

        if request.method == 'POST':

            directory = request.form['directory']

            #target folder

            # if user left the field blank we will save at standard (username) dir
            if directory == "":
                target = os.path.join(APP_ROOT, "images/{}/".format(session['username']))
                directory = session['username']
            else:
                target = os.path.join(APP_ROOT, "images/{}/{}/".format(session['username'], directory))

            # if the images directory does not exist we will make it
            if not os.path.isdir(target):
                os.mkdir(target)

            # go through the list of files uploaded by user
            for img in request.files.getlist("image"):

                filename = img.filename
                caption = request.form['caption']

                destination = ''.join([target, filename])


                # verify the file type, we want to save only jpg and png files
                extension = os.path.splitext(filename)[1].lower()

                if (extension != '.jpg') and (extension != '.png'):
                    return render_template('upload_image.html', msg="You can upload only .jpg and .png files")


                # if image was stored in the database (return value was True)
                # then we will actually save the image in specified location
                if Image.new_image(session['username'], caption, filename, directory):

                    img.save(destination)
                    return render_template('upload_image.html', msg="Images uploaded.")

                #filename was already in the current user directory
                else:
                    return render_template('upload_image.html', msg="Image is already uploaded.")


        # if request.method=='GET'
        else:
            return render_template('upload_image.html', msg="")

    # if user has not logged in then we redirect them to the login page
    else:
        return render_template('login.html')


# return render_template('gallery.html', image_names=os.listdir('src/images/{}/'.format(session['username'])))


@app.route('/image/<filename>')
def show_image(filename):

    return send_from_directory('images/{}'.format(session['username']), filename)


@app.route('/gallery', methods=['GET'])
def show_images():

    #image_names = os.listdir('src/images/{}/'.format(session['username']))

    images = Image.images_from_mongo(session['username']) # returns a list of image objects for given username

    image_file_names = []

    for image in images:
        image_file_names.append(image.filename)

    print(image_file_names)

    return render_template("gallery.html", image_names=image_file_names)



if __name__ == '__main__':
    app.run(debug=True)
