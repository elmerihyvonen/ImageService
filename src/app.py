import secrets
from flask import Flask, url_for, render_template, session, send_from_directory, flash, request, abort
import os
import shutil
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.utils import redirect
from src.common.database import Database
from src.models.image import Image
from src.models.user import User
from src.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm
from flask_bcrypt import Bcrypt


__author__ = "Elmeri Hyvönen"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# 'src/'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# before anything we need to initialize the database first
@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/')
def home():
    return render_template("home.html", images=all_images())

# ---------------------------------------------------------------------------------------------------------------------

@login_manager.user_loader
def load_User(user_id):
    user = User.get_by_id(user_id)
    if user is not None:
        return user
    else:
        return None

# ---------------------------------------------------------------------------------------------------------------------

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

            log_user = User(find_user['username'], find_user['password'], find_user['profile_image'], find_user['_id'])
            login_user(log_user, remember=form.remember.data)
            next_page = request.args.get('next')
            User.login(username)
            flash('Login successful', 'success')

            return redirect(next_page) if next_page else redirect(url_for('home'))

        # if login was not valid session['email'] should be None
        else:
            session['username'] = None
            flash('Check your credentials.', 'danger')

    return render_template('login.html', title='Login', form=form)

# --------------------------------------------------------------------------------------------------------------------

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
            flash(f'Account for username: {username}. You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Username: {username} is already in use', 'danger')

    return render_template('register.html', form=form)

# --------------------------------------------------------------------------------------------------------------------

@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('You have been logged out of ImageService.', 'success')
    return redirect(url_for('home'))


# ---------------------------------------------------------------------------------------------------------------------

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_images():

    form = PostForm()

    if form.validate_on_submit():

        img = form.picture.data
        filename = img.filename
        caption = form.caption.data

        # verify the file type, we want to save only jpg, jpeg and png files
        extension = os.path.splitext(filename)[1].lower()
        if (extension != '.jpg') and (extension != '.png') and (extension != '.jpeg'):
            flash('You can upload only .jpg, .jpeg and .png files', 'danger')
            return redirect(url_for('upload_images'))

        # if image was stored in the database (return value was True)
        # then we will save the image in specified location
        if Image.new_image(current_user.username, caption, filename, current_user.profile_image):
            target = os.path.join(APP_ROOT, "static/images", filename)
            img.save(target)
            flash('Image posted.', 'success')
            return render_template('home.html', images=all_images())

        #filename was already in the current user directory
        else:
            flash('Image is already posted by you.', 'danger')

    return render_template('upload_image.html', form=form, legend='New Post')


# ------------------------------------------------------------------------------------------------------------

@app.route('/image/<filename>')
def show_image(filename):
    return send_from_directory('static/images/', filename)

# --------------------------------------------------------------------------------------------------------------

@app.route('/gallery', methods=['GET'])
@login_required
def show_images():

    # returns a list of image objects for given username
    images = Image.images_from_mongo(current_user.username)
    images.reverse()

    profile_pic = url_for('static', filename='profile_pics/{}'.format(current_user.profile_image))

    return render_template("gallery.html", images=images, profile_pic=profile_pic)

# ---------------------------------------------------------------------------------------------------------------

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateProfileForm()
    if form.validate_on_submit():

        user1 = User.get_by_username(form.username.data)
        if user1 and (current_user.username != form.username.data):

            flash(f'Username: {form.username.data} is already in use', 'danger')
            return redirect(url_for('account'))

        user = User.get_by_username(current_user.username)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            old_profile_image = current_user.profile_image
            current_user.profile_image = picture_file

            # lets remove the file that is no longer needed
            if old_profile_image != 'Anonyymi.jpeg':
                target = os.path.join(APP_ROOT, "static/profile_pics/{}".format(old_profile_image))
                os.remove(target)

        old_username = current_user.username

        if form.username.data:
            current_user.username = form.username.data

        user.update_profile(new_username=current_user.username,
                            old_username=old_username,
                            new_profile_image=current_user.profile_image)

    elif request.method == 'GET':
        form.username.data = current_user.username

    profile_pic = url_for('static', filename='profile_pics/{}'.format(current_user.profile_image))
    return render_template('account.html', title='Account', profile_pic=profile_pic, form=form)

# ---------------------------------------------------------------------------------------------------------------

# makes a random hex filename to avoid situations when there are two files
# in profile_pics folder with the same name
def save_picture(profile_pic):

    hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(profile_pic.filename)
    pic_filename = hex + file_ext
    target = os.path.join(APP_ROOT, "static/profile_pics", pic_filename)
    profile_pic.save(target)
    return pic_filename

# ------------------------------------------------------------------------------------------------------------------

@app.route('/gallery/image/<image_id>')
def image(image_id):
    image = Image.get_by_id(image_id)
    return render_template("image.html", image=image)

# -------------------------------------------------------------------------------------------------------------------


@app.route('/delete/<image_id>')
@login_required
def delete_image(image_id):

    image = Image.get_by_id(image_id)

    image.delete_image()

    # to save memory we should delete the actual image file as well
    target = os.path.join(APP_ROOT, "static/images/{}".format(image.filename))
    os.remove(target)

    return render_template("gallery.html", images=Image.images_from_mongo(current_user.username),
                           profile_pic=url_for('static', filename='profile_pics/{}'.format(current_user.profile_image)))

# -------------------------------------------------------------------------------------------------------------------

# return a list of all images for the front page
def all_images():
    images = Image.all_images()
    images.reverse()
    return images

# -------------------------------------------------------------------------------------------------------------------

@app.route('/account/delete/<user_id>')
@login_required
def delete_account(user_id):

    user = User.get_by_id(user_id)
    User.delete_user(user_id)

    images = Image.images_from_mongo(user.username)
    Image.delete_images(user.username)

    # delete images from folder
    for image in images:
        target = os.path.join(APP_ROOT, 'static/images/{}'.format(image.filename))
        os.remove(target)

    # delete the profile_pic as well
    if user.profile_image != 'Anonyymi.jpeg':
        target2 = os.path.join(APP_ROOT, "static/profile_pics/{}".format(user.profile_image))
        os.remove(target2)

    # log out
    session.clear()
    logout_user()

    flash('Your account and all images associated with it are now deleted', "success")
    return render_template("home.html", images=all_images())


# --------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run()
