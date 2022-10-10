# from ctypes import addressof
# import email
from app import app
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime

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
            if request.method == 'POST':
                docname = request.form['idproof']
            
            fname = os.path.splitext(file.filename)[0]
            pathh = "~/Documents/VScode/Task3/uploads/"
            url = pathh + fname
            cursor=mysql.connection.cursor()
            user=session['email']
            cursor.execute("select stud_id from student where email=%s",(user, ))
            data = cursor.fetchone()
            studid = int(data[0])
            cursor.execute('INSERT INTO documents(doc_name,url,stud_id) VALUES (% s, % s, % s )', (docname,url,studid))
            mysql.connection.commit()

    except RequestEntityTooLarge:
        return 'File is larger than 16MB limit.'

    return render_template('documents.html', msg=msg)

@app.route('/documents')
def documents():
    return render_template('documents.html')

@app.route('/feestructure')
def feestructure():
    return render_template('feestructure.html')

@app.route('/payment_method')
def payment_method():
    cursor=mysql.connection.cursor()
    user=session['email']
    cursor.execute("select stud_id,class from student where email=%s",(user, ))
    data = cursor.fetchone()
    data1 = int(data[1])
    # print(data)
    if (data1 < 5):
        fee = 3000
    elif (data1 < 8):
        fee = 5000
    elif (data1 < 11):
        fee = 7000
    else:
        fee = 10000

    stud_id = int(data[0])
    date = datetime.now()
    # print(date)
    cursor.execute('INSERT INTO fees(amount,stud_id,date) VALUES (% s, % s, % s )', (fee,stud_id,date))
    mysql.connection.commit()
    # print(amount)
    return render_template('payment_method.html',data=data,fee=fee)

@app.route('/proceed_payment')
def proceed_payment():
    return render_template('proceed_payment.html')

@app.route('/successful')
def successful():
    return render_template('successful.html')



#Admin stuff

@app.route('/admin_login', methods =['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE email = % s AND password = % s', (email, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            # session['id'] = account['id']
            session['email'] = account['email']
            msg = 'Logged in successfully !'
            # user=request.form.get('username')
            return redirect(url_for('admin_dashboard'))
        else:
            msg = 'Incorrect email / password !'
    return render_template('admin_login.html', msg = msg)

@app.route('/admin_logout')
def admin_logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('admin_login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    cursor=mysql.connection.cursor()
    user=session['email']
    cursor.execute("select admin_id,admin_name,email from admin where email=%s",(user, ))
    data= cursor.fetchone()
    return render_template('admin_dashboard.html',data=data)

@app.route('/student_details')
def student_details():
    return render_template('student_details.html')
    