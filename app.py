from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import re
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key' # Replace with a strong secret key

db = SQLAlchemy(app)

# Custom Jinja2 filter to convert newlines to paragraphs
def nl2p(value):
    # Normalize all types of newlines to \n, then split into lines
    lines = value.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    paragraphs = []
    current_paragraph = []

    for line in lines:
        if line.strip():  # If the line is not empty (after stripping whitespace)
            current_paragraph.append(line.strip())
        else:  # If it's an empty line, it signifies a paragraph break
            if current_paragraph:
                paragraphs.append(f'<p>{" ".join(current_paragraph)}</p>')
                current_paragraph = []

    # Add the last paragraph if it exists
    if current_paragraph:
        paragraphs.append(f'<p>{" ".join(current_paragraph)}</p>')

    return '\n'.join(paragraphs)

app.jinja_env.filters['nl2p'] = nl2p

# Database models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create tables and add admin user
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('Apple88', method='pbkdf2:sha256')
        admin_user = User(username='admin', password=hashed_password)
        db.session.add(admin_user)
        db.session.commit()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def highlight_text(text, query):
    if not query:
        return text
    # Escape special characters in the query for regex
    escaped_query = re.escape(query)
    # Use re.sub to wrap occurrences of the query with a span tag
    # re.IGNORECASE makes the search case-insensitive
    return re.sub(f'({escaped_query})', r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            post = Post(title=title, content=content)
            db.session.add(post)
            db.session.commit()
        return redirect(url_for('index'))

    # GET request — handle search
    query = request.args.get('q', '').strip()
    if query:
        posts_query = Post.query.filter(
            (Post.title.ilike(f"%{query}%")) | (Post.content.ilike(f"%{query}%"))
        ).order_by(Post.id.desc()).all()
        
        # Apply highlighting to titles and content
        for post in posts_query:
            post.title = highlight_text(post.title, query)
            post.content = highlight_text(post.content, query)
        posts = posts_query
    else:
        posts = Post.query.order_by(Post.id.desc()).all()

    return render_template('index.html', posts=posts, query=query)

@app.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(basedir, 'static/uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        image_url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({'image_url': image_url})
    return jsonify({'error': 'Something went wrong'}), 500

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('static/uploads', filename)
        file.save(os.path.join(basedir, file_path))

        # Create a new post for the uploaded file
        title = filename
        content = ''
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            content = f'<img src="{url_for('static', filename='uploads/' + filename)}" alt="{filename}">'
        else:
            content = f'<a href="{url_for('static', filename='uploads/' + filename)}">{filename}</a>'
        
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)