from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:T0mat0Pa5t3@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'iVt7IDUZnCP28HjQYgDa5'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
       
    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return '<User %r>' % self.email

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


@app.route('/', methods=['GET'])
def index():
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.filter_by(id=user_id).first()
        user_blogs = Blog.query.filter_by(owner_id=user.id)
        return render_template('dynamic_index.html', 
            site_title="Posts from {0}".format(user.username), 
            user_blogs=user_blogs, user=user)
        
    else:   
        users = User.query.all()
        return render_template('index.html', site_title="Home Page", 
            users=users)

@app.route('/blog', methods=['GET'])
def blog():
    if "id" in request.args:
        blog_id = request.args.get("id")
        blog = Blog.query.filter_by(id=blog_id).first()
        user_id = blog.owner_id
        user = User.query.filter_by(id=user_id).first()
        return render_template('dynamic_blog.html', site_title="Blog post", 
            blog=blog, user=user)
        
    else:   
        blogs = Blog.query.all()
        users = User.query.all()
        return render_template('blog.html', site_title="Blog Listings", 
            blogs=blogs, users=users)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        username = session['username']
        current_user = User.query.filter_by(username=username).first()

        title_error = ""
        body_error = ""

        if blog_title == "":
            title_error = "Please enter a title"
        if blog_body == "":
            body_error = "Please enter a body"

        if blog_title == "" or blog_body == "":
            return render_template('newpost.html', site_title="Create a Blog Post", 
            blog_title=blog_title, title_error=title_error, 
            blog_body=blog_body, body_error=body_error)

        #TODO: put the current user as the owner in this declaration
        new_blog = Blog(blog_title, blog_body, current_user)
        db.session.add(new_blog)
        db.session.commit()

        new_post_id = new_blog.id
        
        return redirect('/blog?id={0}'.format(new_post_id))

    return render_template('newpost.html', site_title="Create a Blog Post")


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash('Success! Logged in!')
            return redirect('/newpost')

        elif user:
            flash('Password is incorrect', 'error')

        else:
            flash('Username does not exist', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "" or password == "" or verify == "":
            flash('One or more fields were left empty. Please fill all fields.')

        if password != verify:
            flash('Passwords do not match', 'error')

        if len(username) < 3:
            flash('Invalid username', 'error')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("Signed Up!")
            return redirect('/newpost')

        else:
            flash('That username is alread being used', 'error')

    return render_template('signup.html')


if __name__ == '__main__':
    app.run()