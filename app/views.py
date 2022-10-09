# from ctypes import addressof
# import email
from app import app
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app.config['SECRET_KEY'] = "my super secret key"

#connect to mysql db
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'AbhiK@1998'
app.config['MYSQL_DB'] = 'school_db'

#for file upload
app.config['UPLOAD_DIRECTORY'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 *1024
app.config['ALLOWED_EXTENSIONS'] = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE email = % s AND password = % s', (email, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            # session['id'] = account['id']
            session['email'] = account['email']
            msg = 'Logged in successfully !'
            # user=request.form.get('username')
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect email / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        year = request.form['year']
        fname = request.form['fname']
        mname = request.form['mname']
        classs = request.form['class']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email or not dob or not gender or not phone or not year or not address or not fname or not mname or not classs:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO student(stud_name,dob,gender,address,email,contact,year,f_name,m_name,password,class) VALUES ( % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s )', (username, dob, gender, address, email, phone, year, fname, mname, password, classs, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'

    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/dashboard')
def dashboard():
    #print('success')
    cursor=mysql.connection.cursor()
    user=session['email']
    #print(user)
    cursor.execute("select stud_id,stud_name,dob,gender,address,email,contact,year,f_name,m_name,class from student where email=%s",(user, ))
    data= cursor.fetchone()
    # print(data)
    # nam=session.get('email',None)
    # print(nam)
    return render_template('dashboard.html',data=data)
    

@app.route('/upload', methods =['GET', 'POST'])
def upload():
    msg=''
    try:
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
    
        if file:
            if extension not in app.config['ALLOWED_EXTENSIONS']:
                return 'Unsupported file format !'

            file.save(os.path.join(app.config['UPLOAD_DIRECTORY'],secure_filename(file.filename)))
            msg = 'File Uploaded Successfully !'
            # user=session['email']
            

    except RequestEntityTooLarge:
        return 'File is larger than 16MB limit.'

    return render_template('documents.html', msg=msg)

@app.route('/documents')
def documents():
    return render_template('documents.html')

