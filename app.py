from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from database import init_db, add_item, search_items, claim_item, get_all_items, add_user, verify_password
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'), static_folder='static')
app.secret_key = 'your_secret_key_here'

# Folder for storing uploaded images
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize DB
init_db()


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


# Load user from DB
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None


# Helper function for file type check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
@login_required
def home():
    items = get_all_items()
    return render_template('home.html', items=items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = verify_password(username, password)
        if user:
            login_user(User(user[0], user[1]))
            return redirect(url_for('home'))
        flash('Invalid credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            add_user(username, password)
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/report_lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        reporter_name = request.form['reporter_name']
        contact = request.form['contact']

        # Handle image upload
        image_file = request.files['image']
        image_filename = None
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        add_item(name, description, location, reporter_name, contact, 'lost', current_user.id, image_filename)
        flash('Lost item reported successfully!')
        return redirect(url_for('home'))
    return render_template('report_lost.html')


@app.route('/report_found', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        finder_name = request.form['finder_name']
        contact = request.form['contact']

        # Handle image upload
        image_file = request.files['image']
        image_filename = None
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        add_item(name, description, location, finder_name, contact, 'found', current_user.id, image_filename)
        flash('Found item reported successfully!')
        return redirect(url_for('home'))
    return render_template('report_found.html')


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    results = []
    if request.method == 'POST':
        query = request.form['query']
        results = search_items(query)
    return render_template('search.html', results=results)


@app.route('/claim/<int:item_id>')
@login_required
def claim(item_id):
    claim_item(item_id)
    flash('Item claimed!')
    return redirect(url_for('home'))


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
