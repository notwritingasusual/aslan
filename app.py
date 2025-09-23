from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import re

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Custom Jinja2 filter to convert newlines to paragraphs
def nl2p(value):
    # Replace all sequences of newlines with a single newline
    value = re.sub(r'(\r\n|\r|\n)+', '\n', value).strip()
    # Split by newline and wrap each line in a paragraph tag
    paragraphs = [f'<p>{p.strip()}</p>' for p in value.split('\n')]
    return '\n'.join(paragraphs)

app.jinja_env.filters['nl2p'] = nl2p

# Database model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
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
        posts = Post.query.filter(
            (Post.title.ilike(f"%{query}%")) | (Post.content.ilike(f"%{query}%"))
        ).order_by(Post.id.desc()).all()
    else:
        posts = Post.query.order_by(Post.id.desc()).all()

    return render_template('index.html', posts=posts, query=query)

if __name__ == '__main__':
    app.run(debug=True)
