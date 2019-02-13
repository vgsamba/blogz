from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://buildablogs:buildablogs@localhost:8889/buildablogs'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):  # inherits basic funtionality fromm MODEL

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))  # another column in table
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blogdetails():
    blogid = request.args.get('id')
    if blogid is not None:
        blog = Blog.query.get(blogid)
        return render_template('BlogEntryDetails.html', title=blog.title, body=blog.body)
    blogpost = Blog.query.all()
    return render_template('blog.html', title="Build a blog!", blogpost=blogpost)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    blog_title = ''
    blog_body = ''
    titleerror = ''
    bodyerror = ''
    if request.method == 'POST':

        blog_title = request.form['title']
        blog_body = request.form['body']

        if (not blog_title) or (blog_title.strip() == ""):
            titleerror = "Please enter a valid Title for the blog"
        if (not blog_body) or (blog_body.strip() == ""):
            bodyerror = "Please enter a valid content for the blog"
        if titleerror or bodyerror:
            return render_template('newpost.html', blogtitle=blog_title, blogbody=blog_body, titleerror=titleerror,
                                   bodyerror=bodyerror)

        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()  # replace string functionality with db

        return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html', blogtitle=blog_title, blogbody=blog_body)


if __name__ == '__main__':
    app.run()