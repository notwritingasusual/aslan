
import os
import sys

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

from app import db, Post, app

with app.app_context():
    posts = Post.query.all()
    for post in posts:
        print(f"ID: {post.id}, Title: {post.title}")
