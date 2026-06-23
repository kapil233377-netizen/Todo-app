from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "todo_app_secret_key_2026"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return self.username


class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)

    date_created = db.Column(
        db.DateTime,
        default=datetime.now
    )
    
    completed = db.Column(
    db.Boolean,
    default=False
)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.sno'),
        nullable=False
    )

    def __repr__(self):
        return f"{self.sno}"
    
   

# ================= DASHBOARD =================

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')


    user_id = session['user_id']


    total_todos = Todo.query.filter_by(
        user_id=user_id
    ).count()


    completed_todos = Todo.query.filter_by(
        user_id=user_id,
        completed=True
    ).count()


    pending_todos = Todo.query.filter_by(
        user_id=user_id,
        completed=False
    ).count()
    
    if total_todos > 0:
        progress = int((completed_todos / total_todos) * 100)
    else:
        progress = 0


    recent_todos = Todo.query.filter_by(
        user_id=user_id
    ).order_by(
        Todo.date_created.desc()
    ).limit(5).all()


    return render_template(
        'dashboard.html',
        total_todos=total_todos,
        completed_todos=completed_todos,
        pending_todos=pending_todos,
        progress=progress,
        recent_todos=recent_todos,
        username=session.get('username')
    )
        
@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        if 'user_id' not in session:
            flash(
                "Please Login or Create Account to add todos.",
                "warning"
            )
            return redirect('/login')

        title = request.form['title']
        desc = request.form['desc']

        todo = Todo(
            title=title,
            desc=desc,
            user_id=session['user_id']
        )

        db.session.add(todo)
        db.session.commit()

        flash("Todo Added Successfully ✅", "success")

        return redirect('/')

    search = request.args.get('search')

    if 'user_id' in session:

        if search:
            allTodo = Todo.query.filter(
                Todo.user_id == session['user_id'],
                Todo.title.contains(search)
            ).all()

        else:
            allTodo = Todo.query.filter_by(
                user_id=session['user_id']
            ).all()

    else:

        allTodo = []

    return render_template(
        'index.html',
        allTodo=allTodo
    )   
   
@app.route('/about')
def about():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template('about.html')

@app.route('/contact')
def contact():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template('contact.html')
# ================= SIGNUP =================

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists!", "danger")
            return redirect('/signup')

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account Created Successfully!", "success")

        return redirect('/login')

    return render_template('signup.html')


# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session['user_id'] = user.sno
            session['username'] = user.username

            flash("Login Successful!", "success")

            return redirect('/dashboard')

        flash("Invalid Email or Password", "danger")

    return render_template('login.html')


# ================= LOGOUT =================

@app.route('/logout')
def logout():

    session.clear()

    flash("Logged Out Successfully", "info")

    return redirect('/login')

# ================= COMPLETE TODO =================

@app.route('/complete/<int:sno>')
def complete(sno):

    if 'user_id' not in session:
        return redirect('/login')


    todo = Todo.query.filter_by(
        sno=sno,
        user_id=session['user_id']
    ).first()


    if todo:

        todo.completed = not todo.completed

        db.session.commit()

        flash("Todo Status Updated ✅", "success")

    else:

        flash("Unauthorized Access!", "danger")


    return redirect('/')

@app.route('/delete/<int:sno>')
def delete(sno):

    if 'user_id' not in session:
        return redirect('/login')


    todo = Todo.query.filter_by(
        sno=sno,
        user_id=session['user_id']
    ).first()


    if todo:

        db.session.delete(todo)
        db.session.commit()

        flash("Todo Deleted Successfully 🗑️", "danger")

    else:

        flash("Unauthorized Access!", "danger")


    return redirect('/')



@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):

    if 'user_id' not in session:
        return redirect('/login')


    todo = Todo.query.filter_by(
        sno=sno,
        user_id=session['user_id']
    ).first()


    if not todo:

        flash("Unauthorized Access!", "danger")

        return redirect('/')


    if request.method == 'POST':

        todo.title = request.form['title']
        todo.desc = request.form['desc']


        db.session.commit()

        flash("Todo Updated Successfully ✏️", "warning")


        return redirect('/')


    return render_template(
        'update.html',
        todo=todo
    )


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)