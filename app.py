import sqlite3
import os
from flask import Flask, render_template, request, flash, url_for, session, redirect, abort, g, make_response
from FDataBase import FDataBase
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegistrationForm
from admin.admin import admin


DATABASE = '/tmp/eshop.db'
DEBUG = True
SECRET_KEY = 'figjerig0rei9jg39jg08h348hf9nwf0if0'
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'eshop.db')))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to get access to this page.'
login_manager.login_message_category = 'success'

@login_manager.user_loader
def load_user(user_id):
    print('load user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('tables.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


#Pages
@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', title='eShop', auth=current_user.is_authenticated, item_list=dbase.getRecentItems())


@app.route('/catalog')
def catalog():
    return render_template('catalog.html', title='Catalog', auth=current_user.is_authenticated, item_list=dbase.getList())


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/add-item', methods=['POST', 'GET'])
def add_item():
    if request.method == 'POST':
        if len(request.form['title'])>2 and float(request.form['price'])>0:
            if 'image' not in request.files:
                flash('No file part')
            file = request.files['image']
            if file.filename == '':
                flash('No selected image')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_name_part = [app.config['UPLOAD_FOLDER'], filename.split('.')[-1]]

                res = dbase.addItem(request.form['title'], request.form['price'], request.form['description'], image_name_part)
                file.save(dbase.getImage()[0])

                if not res:
                    flash('Add error', category='error')
                else:
                    flash('Item added successfully!', category='success')
        else:
            flash('Add error', category='error')

    return render_template('add_item.html', title='Add item', auth=current_user.is_authenticated)


@app.route('/item/<int:id_item>')
@login_required
def show_item(id_item):
    title, price, description, image_url, stock = dbase.getItem(id_item)
    print(title, f"{price:.2f}", description, image_url, stock)
    if not title:
        abort(404)

    return render_template('item_page.html', title=title, auth=current_user.is_authenticated, price=f"{price:.2f}", description=description, image_url=image_url[7:], stock=stock)


@app.route('/contact-us', methods=['POST', 'GET'])
def contact_us():
    if request.method=='POST':
        if len(request.form['username'])>2 and len(request.form['message'])>5:
            print(request.form)
            flash('Message sent successfully!', category='success')
        else:
            flash('Sending error', category='error')

    return render_template('contact_us.html', title='Contact Us', auth=current_user.is_authenticated)


@app.route('/about')
def about():
    return render_template('about.html', title='About', auth=current_user.is_authenticated)

# @app.route('/profile/<username>')
# def profile(username):
#     if 'userLogged' not in session or session['userLogged']!=username:
#         abort(401)
#     return f'User {username}'


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByLogin(form.login.data)
        if user and check_password_hash(user['password'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash('Login or password is incorrect', 'error')

    return render_template('login.html', title='Login', auth=current_user.is_authenticated, form=form)

    # if request.method == 'POST':
    #
    #
    # return render_template('login.html', title='Login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if len(form.login.data)>=3 and len(form.email.data)>4 \
            and len(form.psw.data)>=3 and form.agr.data:
            hash = generate_password_hash(form.psw.data)
            res = dbase.addUser(form.login.data, form.email.data, hash)
            if res:
                flash('You registered successfully!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration error', 'error')
        else:
            flash('Registration error, check for correctness', 'error')

    return render_template('register.html', title='Registration', auth=current_user.is_authenticated, form=form)


    # if request.method == 'POST':
    #     if len(request.form['login'])>=3 and len(request.form['email'])>4 \
    #         and len(request.form['psw'])>=3 and request.form['psw']==request.form['psw2']:
    #         hash = generate_password_hash(request.form['psw'])
    #         res = dbase.addUser(request.form['login'], request.form['email'], hash)
    #         if res:
    #             flash('You registered successfully!', 'success')
    #             return redirect(url_for('login'))
    #         else:
    #             flash('Registration error', 'error')
    #     else:
    #         flash('Registration error, check for correctness', 'error')
    # return render_template('register.html', title='Registration')



    # log = ''
    # if request.cookies.get('logged'):
    #     log = request.cookies.get('logged')
    # # if 'userLogged' in session:
    # #     return redirect(url_for('profile', username=session['userLogged']))
    # # elif request.method == 'POST' and request.form['username']=='max' and request.form['psw']=='123':
    # #     session['userLogged'] = request.form['username']
    # #     return redirect(url_for('profile', username=session['userLogged']))
    # res = make_response(render_template('login.html', title='Login', logged=log))
    # res.set_cookie('logged', 'yes', 7*24*3600)
    # return res


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out successfully', 'success')
    return redirect('login')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile', user=current_user, auth=current_user.is_authenticated)


# @app.route('/logout')
# @login_required
# def logout():
#     res = make_response(redirect('/login'))
#     res.set_cookie('logged', '', 0)
#     return res


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Page not found', auth=current_user.is_authenticated), 404


if __name__ == '__main__':
    app.run(debug=True)
