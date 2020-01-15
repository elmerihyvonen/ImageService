from flask import Flask, request, url_for, render_template, session, send_from_directory, flash
import os
from flask_login import LoginManager, login_user, logout_user, current_user
from werkzeug.utils import redirect
from src.common.database import Database
from src.models.image import Image
from src.models.user import User
from src.forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt


__author__ = "Elmeri Hyvönen"


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a3cac62b7421cb1dcd4208f9e6c51937'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


# 'src/'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# before anything we need to initialize the database first
@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/')
def home():
    return render_template("home.html")

@login_manager.user_loader
def load_User(user_id):
    user = User.get_by_id(user_id)
    if user is not None:
        return user
    else:
        return None


@app.route('/login', methods=['POST', 'GET'])
def login():

    # if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']

        find_user = Database.find_one('users', {'username': username})

        # checks if the login is valid
        if User.login_valid(username, password, bcrypt):

            loguser = User(find_user['username'], find_user['password'], find_user['_id'])
            login_user(loguser, remember=form.remember.data)
            User.login(username)
            flash('Login successful', 'success')
            return redirect(url_for('home'))

        # if login was not valid session['email'] should be None
        else:
            session['email'] = None
            flash('Check your credentials.', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():

    # if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))


    form = RegistrationForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        # creates a hashed password from password that user typed
        # and decodes it to string. Then we can store the hashed password to database.
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # if return value is False then the 'username' is already in use
        if User.register(username, hashed_password):
            flash(f'Account for: {username} created. You can now log in.', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Username: {username} is already in use', 'danger')

    return render_template('register.html', form=form)

# ----------------------------------------------------------------------

@app.route('/logout')
def logout():
    session.clear()
    logout_user()
    flash('You have been logged out of ImageService.', 'success')
    return redirect(url_for('home'))


# ----------------------------------------------------------------------

@app.route('/upload', methods=['GET', 'POST'])
def upload_images():

    # lets first verify that user has logged in
    if session['username'] is not None:

        if request.method == 'POST':


            target = os.path.join(APP_ROOT, "images/{}/".format(session['username']))

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

                if (extension != '.jpg') and (extension != '.png') and (extension != '.jpeg'):
                    flash('You can upload only .jpg, .jpeg and .png files', 'danger')

                # if image was stored in the database (return value was True)
                # then we will actually save the image in specified location
                if Image.new_image(session['username'], caption, filename):

                    img.save(destination)
                    flash('Images uploaded.', 'success')

                #filename was already in the current user directory
                else:
                    flash('Image is already uploaded.', 'danger')

        return render_template('upload_image.html')

    # if user has not logged in then we redirect them to the login page
    else:
        return render_template('login.html')


# return render_template('gallery.html', image_names=os.listdir('src/images/{}/'.format(session['username'])))


@app.route('/image/<filename>')
def show_image(filename):

    return send_from_directory('images/{}'.format(session['username']), filename)


@app.route('/gallery', methods=['GET'])
def show_images():

    images = Image.images_from_mongo(session['username']) # returns a list of image objects for given username

    image_file_names = []

    for image in images:
        image_file_names.append(image.filename)

    return render_template("gallery.html", image_names=image_file_names)




if __name__ == '__main__':
    app.run(debug=True)
