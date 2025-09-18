from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Store posts in memory for now
posts = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            posts.append({'title': title, 'content': content})
        return redirect(url_for('index'))
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
