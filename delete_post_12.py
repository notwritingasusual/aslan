
import os
import sys

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

from app import db, Post, app

# Post ID to delete
post_id_to_delete = 12

with app.app_context():
    post = Post.query.get(post_id_to_delete)
    if post:
        db.session.delete(post)
    db.session.commit()

print(f"Deleted post with ID: {post_id_to_delete}")
