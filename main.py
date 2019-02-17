from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)  #app instance of sqlalchemy
app.secret_key= "12345qwer"  #to be used with sessions


class Blog(db.Model):  # inherits basic funtionality fromm MODEL

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))  # another column in table
    body = db.Column(db.Text)
    owner_id=db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):  #owner is object. every blog has an owner
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):                                         #Add User Class---- COVERED
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username , password):
        self.username =username
        self.password=password

@app.route('/login', methods=['POST', 'GET'])
def login():

    passworderror=''
    user_error=''
    if request.method=='POST':
        username=request.form['username'] # dictionary that contains post request
        password=request.form['password']
        user=User.query.filter_by(username=username).first() # Query to retieve that valid user
        # not valid then will return spl vatiable called none
        if user and user.password== password: # does user exists
            #TODO remember user logged in
            session['username']=username  # session is an object that is used to store
            #associated with one specific users, one request to another
            #session username dictionary-will help decide if it remembers the user
            flash('logged in '+username)
                                         # todo A Note About Use Cases --covered
            return redirect('/newpost') # return to newpost page
        elif user and user.password != password:
            # todo login failed
            passworderror='Your password is incorrect'

        else: #user is not None and user.username != username:  # when user name is not exists
            flash('user does not exists')
            #user_error='Username does not exists'
    return render_template('login.html',passworderror=passworderror) #user_error=user_error)

#@app.route('/logout')
#def logout():
    #print('user logged is', username)
    # remove the username from the session if it is there
    ##print('user logedout i', username)
    #return redirect(url_for('/blog')) #  basically remove user  email from session on logout

    # if 'username' in session:
    #     username = session['username']
    #     userlogout=User.query.get(username)
    #     db.session.delete(userlogout)
    #     db.session.commit()

#    return redirect('/blog')
@app.route("/logout")  #TODO add a require_login function and decorate it with @app.before_request
def logout():
    del session['username']
    return redirect('/blog')  # todo able to logout ---- done

  # TODO Validation FOR SIGN UP PAGE

def validate(fieldname, fieldval, fieldlen):
    msg = ''
    if (not fieldval) or (fieldval.strip() == "") or (" " in fieldval) or (fieldlen < 3) or (fieldlen > 20):
        msg = "Please enter a valid " + fieldname
    return msg

@app.route('/signup', methods=['POST', 'GET'])
def signup():      #create account

    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        user_name_length = len(username)
        password_length = len(password)
        username_error = validate("username", username, user_name_length)
        password_error = validate("password", password, password_length)
        confirmpassword_error = ''

        if not password == confirm_password or confirm_password.strip() == "":
            confirmpassword_error = "Passwords do not match"

        user=User.query.filter_by(username=username).first()
        #if not username_error and user:

        if user is not None and user.username == username:
            username_error="User already exists"

        if not username_error and not password_error and not confirmpassword_error:
            #return render_template('welcome_page.html', name=user_name)
            new_user=User(username, password)# create new
            db.session.add(new_user)
            db.session.commit()
            session['username']=username
            flash('logged in '+username)
            return redirect('/newpost')
        else:
            return render_template('signup.html', username=username,
                                   username_error=username_error,
                                   password_error=password_error,
                                   confirmpassword_error=confirmpassword_error)
    return render_template('signup.html')



@app.route('/')
def index():
    #username = request.args.get('username')
    #users_list=User.query.filter_by(username)
    #return render_template('index.html',users_list)
    if username is not None:
        user=User.query.filter_by(username=username).first()
        users.append(user)
        return render_template('blog.html', title="Build a blog!", users=users)

        users = User.query.all()
        return render_template('blog.html', title="Build a blog!", users=users)
    users=User.query.order_by(User.username).all()
    return render_template('index.html', title="Build Users!", users=users)

@app.route('/blog', methods=['GET'])
def blogdetails():

    blogid = request.args.get('id')
    username = request.args.get('user')
    users = []
    #owner_idusername = request.args.get('owner_id.username')
    if blogid is not None:
        blog = Blog.query.get(blogid)
        username=User.query.get(blog.owner_id) #todo get written by signature
        return render_template('BlogEntryDetails.html', title=blog.title, body=blog.body,owner_id= username.username)
    if username is not None:
        user=User.query.filter_by(username=username).first()
        users.append(user)
        return render_template('blog.html', title="Build a blog!", users=users)

    users = User.query.all()
    return render_template('blog.html', title="Build a blog!", users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    blog_title = ''
    blog_body = ''
    titleerror = ''
    bodyerror = ''

    owner= User.query.filter_by (username=session['username']).first()# as user already logged by username id get their session like this

    if request.method == 'POST':

        blog_title = request.form['title']
        blog_body = request.form['body']

        if (not blog_title) or (blog_title.strip() == ""):
            titleerror = "Please enter a valid Title for the blog"
        if (not blog_body) or (blog_body.strip() == ""):
            bodyerror = "Please enter a valid content for the blog"
        if titleerror or bodyerror:
            return render_template('newpost.html', blogtitle=blog_title, blogbody=blog_body, titleerror=titleerror,
                                   bodyerror=bodyerror, owner=owner)

        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()  # replace string functionality with db

        return redirect('/blog?id=' + str(new_blog.id))  # not sure of owner here

    return render_template('newpost.html', blogtitle=blog_title, blogbody=blog_body, owner=owner)




if __name__ == '__main__':
    app.run()