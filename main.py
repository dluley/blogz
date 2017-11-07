from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Unit2Final@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True)
    password = db.Column(db.String(12))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


        
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(900))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'allposts', 'blog', 'index', 'singleuser']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', tab_title="Blog Users", users=users)


@app.route('/login', methods=['POST', 'GET'])
def login():
    message = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in!")
            return redirect('/')
        else:
            message = "User password incorrect, or user does not exist"

    return render_template('login.html', message = message)



@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username = ""
    password = ""
    verify = ""
    username_error = ""
    password_error = ""
    verify_error = ""
    valid_error = ""
    user_error = ""
    switch = False

    if request.method == 'GET':
        return render_template("signup.html", tab_title="Sign-Up")
    
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "":
            switch = True
            username_error = "A username is needed to sign up"

        if password == "" or verify == "":
            switch = True
            password_error = "One or more fields are invalid"

        if password != verify:
            switch = True
            verify_error = "The password and verify password fields do not match"

        if len(username) <= 3 or len(password) <= 3:
            switch = True
            valid_error = "Both username and password must be at least 4 characters long"

        existing_user = User.query.filter_by(username=username).first()

        if existing_user == username:
            switch = True
            user_error = "User already exists"
        
        if switch == True:
            return render_template("signup.html", username=username, username_error=username_error, password=password, password_error=password_error, verify=verify, verify_error=verify_error, valid_error=valid_error, user_error=user_error)
        
        else:

            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username

            return redirect('/')


@app.route('/blog', methods=['GET'])
def blog():
        
    if request.args:
        #user_id = request.args.get('user.username')
        blog_id = request.args['id']
        blog = Blog.query.filter_by(id=blog_id).first()
        #blist.append(blogs)
        #blist.append(Blog.query.get(user_id))
        return render_template('singlepost.html', blog=blog)

    else:
        blogs = User.query.all()

    return render_template('blog.html', tab_title='Blog Users', blogs=blogs)

    #if request.args.get('id'):
        #blog_id = request.args.get('id')
        #blist.append(Blog.query.get(blog_id))
        #view = 'single'
        #return render_template('blog.html', blist=blist, view=view)

    #session['username'] = username
    #view = 'default'        
    #blist = Blog.query.filter_by(owner=owner).all()
        
    #return render_template('blog.html', tab_title='Build-A-Blog', blist=blist, view=view)

@app.route('/allposts', methods=['GET', 'POST'])
def allposts():
    blogs = Blog.query.all()

    if request.args:
        blogs = Blog.query.all()
        #blist = []
        #blist.append(blogs)

        return render_template("allposts.html", blogs=blogs)

    else:
        return render_template("allposts.html", blogs=blogs)



@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    #owner = User.query.filter_by(username=session['username']).first()


    if request.method =='GET':
        blogs = Blog.query.all()
        return render_template('newpost.html', tab_title="Blog Post", blogs=blogs)

    if request.method == 'POST':

        title = ""
        body = ""
        title_error = ""
        body_error = ""
        title = request.form['title']
        body = request.form['body']
        switch = False

        if title == "":
            switch = True
            title_error = "A post must have a title to be submitted"

        if body == "":
            switch = True
            body_error = "A post must have a body to be submitted"

        if switch == False:

            owner = User.query.filter_by(username=session['username']).first()
            new_post = Blog(title, body, owner)
            new_post.title = title
            new_post.body = body

            db.session.add(new_post)
            db.session.commit()
            
            #blist = []
            #number = request.args.get('id')
            blog_url = "/blog?id=" + str(new_post.id)
            return redirect(blog_url)
        
        else:
            return render_template('newpost.html', tab_title="Blog Entry", title=title, title_error=title_error, body=body, body_error=body_error)
        
        #return render_template('blog.html', tab_title='Build-A-Blog', blist=blist, view=view)
            
            #return redirect('/blog?id=number')

    #return render_template('newpost.html', tab_title = 'Add an Entry', title = title, title_error = title_error, body = body, body_error = body_error, owner = owner)




@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/singleuser', methods=['GET'])
def singleuser():
    
    if request.args.get('username'):
        username = request.args.get('username')
        user = User.query.filter_by(username=username).first()

        return render_template('singleuser.html', user=user)

    return render_template('singleuser.html', tab_title="Blog List")

if __name__ == '__main__':
    app.run()