from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)  #app instance of sqlalchemy
app.secret_key= "12345qwer"  #to be used with sessions


# TODO
#Create a Blog class for table blog with id title body  columns
## and owner Id

class Blog(db.Model):  # inherits basic funtionality fromm MODEL

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))  # another column in table
    body = db.Column(db.Text)
    owner_id=db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):  #owner is object. every blog has an owner
        self.title = title
        self.body = body
        self.owner = owner


# TODO
#Create a User class for table user with id username password  columns
## and blogs column to map relationship between user table n blog table

class User(db.Model):                                         #Add User Class---- COVERED
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username , password):
        self.username =username
        self.password=password


# TODO
# Create Function for user Login
@app.route('/login', methods=['POST', 'GET'])
def login():

    passworderror=''
    username=''
    usernameerror=''
    if request.method=='POST':
        username=request.form['username'] # dictionary that contains post request
        password=request.form['password']
        user=User.query.filter_by(username=username).first() # Query to retieve that valid user
        # not valid then will return spl variable called none

        # TODO
        # #validate the user
        # #create a session to remember him for this particular login

        if user and user.password== password: # does user exists
            #TODO remember user logged in
            session['username']=username  # session is an object that is used to store
            #associated with one specific users, one request to another
            #session username dictionary-will help decide if it remembers the user
            flash('logged in '+username)
                                         # todo A Note About Use Cases --covered
            return redirect('/newpost') # return to newpost page

            # todo login failed
        elif user and user.password != password:
            passworderror='Your password is incorrect'

        else: #user is not None and user.username != username:  # when user name is not exists
            usernameerror='user does not exists'

    return render_template('login.html',passworderror=passworderror, usernameerror=usernameerror)


# TODO
# Logout the user
# and delete his session.
#redirect to main blog page- /blog

@app.route("/logout")  #TODO add a require_login function and decorate it with @app.before_request
def logout():
    #del session['username']
    session.clear()
    return redirect('/blog')  # todo able to logout ---- done

  # TODO Validation FOR SIGN UP PAGE

def validate(fieldname, fieldval, fieldlen):
    msg = ''
    if (not fieldval) or (fieldval.strip() == "") or (" " in fieldval) or (fieldlen < 3) or (fieldlen > 20):
        msg = "Please enter a valid " + fieldname
    return msg

# TODO
##Signup() to create an account
# In post method do user entered field validation and display appropriate error msgs on signup.html


@app.route('/signup', methods=['POST', 'GET'])
def signup():

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

        # Valid user craete a session and send to newpost page

        if not username_error and not password_error and not confirmpassword_error:
            new_user=User(username, password)# create new user
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

# TODO
#display all entries when user is on /blog blog.html
# when user clicks on a blog entry , then get that blog id and display in BlogEntryDetails.html page
# Display blog author username at the bottom

@app.route('/blog', methods=['GET'])
def blogdetails():

    blogid = request.args.get('id')
    selected_username = request.args.get('user')
    #users = []
    if blogid is not None:
        blog = Blog.query.get(blogid)
        username=User.query.get(blog.owner_id) #todo get written by signature
        return render_template('BlogEntryDetails.html', title=blog.title, body=blog.body,owner_id= username.username)
    if selected_username is not None:
        user=User.query.filter_by(username=selected_username).first()
        #users.append(user)
        return render_template('singleUser.html', title="singleUser!", user=user)

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

@app.route('/')
def index():
    #return redirect('/blog')
    #username = request.args.get('username')
    #users_list=User.query.filter_by(username)
    #return render_template('index.html',users_list)
    # if username is not None:
    #     user=User.query.filter_by(username=username).first()
    #     users.append(user)
    #     return render_template('blog.html', title="Build a blog!", users=users)
    #
    #     users = User.query.all()
    #     return render_template('blog.html', title="Build a blog!", users=users)
    selected_username = request.args.get('user')
    users = []
    if selected_username is None:
        users=User.query.order_by(User.username).all()
        return render_template('index.html', title="Build Users!", users=users)
    user=User.query.filter_by(username=selected_username).first()
    users.append(user)
    return render_template('blog.html', title="Build a blog!", users=users)

# TODO 5: modify this function to rely on a list of endpoints that users can visit without being redirected.


@app.before_request  # TODO Require Login--to be covered
def require_login():
    print(request.endpoint)
    if request.endpoint == 'newpost' and not 'username' in session:
        return redirect("/login")


if __name__ == '__main__':
    app.run()