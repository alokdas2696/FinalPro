
import os

from flask import Flask, render_template, session,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy, request


from flask_mail import *
import json
from random import randint
app = Flask(__name__)
app.secret_key = "login"


with open('config.json', 'r') as k:
    params = json.load(k)['params']
otp = randint(1111, 9999)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/studb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = params['gmail-user']
app.config['MAIL_PASSWORD'] = params['gmail-password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


class Student(db.Model):
    stuid = db.Column(db.Integer(), unique=True, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    mbno = db.Column(db.String(10), unique=False, nullable=False)
    mtmarks = db.Column(db.Integer(), unique=False, nullable=False)
    scmarks = db.Column(db.Integer(), unique=False, nullable=False)
    csmarks = db.Column(db.Integer(), unique=False, nullable=False)

    def __repr__(self):
        return f"Student('{self.stuid}','{self.name}','{self.email}','{self.mbno}','{self.mtmarks}','{self.scmarks}','{self.csmarks}')"


@app.route('/', methods=['GET'])
def home():
    return render_template("email.html")


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        # email = request.form.get('email')

        d = request.form.get('rollno')
        stuid = Student.query.get(d)
        if stuid == None:
            return "Invalid Roll number ... go back"
        email = stuid.email
        # if email.strip() == email:
       

        if email.strip() == email:
            msg = Message('OTP',sender='alokdas9626@gmail.com', recipients=[email])
            msg.body = str(otp)
            mail.send(msg)
            return render_template("verify.html", d=d)
        else:
            return " Unmatched EmailID with Roll No"
    return render_template('verify.html')


@app.route('/validate/<int:d>',methods=['GET', 'POST'])
def validate(d):
    if request.method == 'POST':
        f = Student.query.get(d)
        gmail = f.email
        userotp = request.form['otp']
        if otp == int(userotp):
            # msg = Message('OTP', sender='alokdas9626@gmail.com', recipients=[gmail])
            # # msg.body = f.name
            # mail.send(msg)

            mail.send_message("Result: ",sender='alokdas9626@gmail.com', recipients=[gmail], body=f.name + "\n Email: " + f.email + "\n Math Marks: " + str(f.mtmarks)
                              + "\n Science Marks: " + str(f.scmarks)+ "\n Computer Marks: " + str(f.csmarks)+ "\n Total Marks:"
                            + str(f.csmarks + f.mtmarks + f.scmarks)+ "\n Percenatge: " +str(round(((f.csmarks + f.mtmarks + f.scmarks)/300)*100)))

            return render_template('result.html',f=f, msg="Result has been Send to your given respected Email Id")
        return render_template('email.html', msg="Not Verified !! try again")


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        if username.strip() == "admin" and password.strip() == "12345":
            session['username'] = username
            return redirect("/admin")
        else:
            msg = " Invalid username/ password"
            return render_template("login.html", msg=msg)
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('email',None)
    return render_template('login.html')


@app.route("/admin",methods=['GET','POST'])
def add():
    if "username" in session:
        if request.method == 'POST':
            stuid = request.form.get('stuid')
            name = request.form.get('name')
            email = request.form.get('email')
            mbno = request.form.get('mbno')
            mtmarks = request.form.get('mtmarks')
            scmarks = request.form.get('scmarks')
            csmarks = request.form.get('csmarks')


            alldata = Student.query.all()
            for student in alldata:

                if student.email == email:
                    flash(f"This data already exits: {email} ", "info")
                    return redirect('/admin')
                elif student.stuid == int(stuid):
                    flash(f"This data already exits: {stuid} ", "info")
                    return redirect('/admin')

            stu = Student(stuid=stuid.strip(), name=name.strip(), email=email.strip(), mbno=mbno.strip(), mtmarks=mtmarks.strip(), scmarks=scmarks.strip(), csmarks=csmarks.strip())

            db.session.add(stu)
            db.session.commit()
        # alldata1 = Student.query.all()

        page = request.args.get('page', 1, type=int)
        # page = request.form.get('page_num')
        alldata1 = Student.query.paginate(page=int(page), per_page=5)

        return render_template('index1.html', alldata1=alldata1)
    else:
        return redirect("/login")

# page = request.args.get('page',1, type=int)
#         # page = request.form.get('page_num')
#         alldata = Student.query.paginate(page=int(page), per_page=10)
@app.route("/update/<int:stuid>" ,methods=['GET','POST'])
def update(stuid):
    if "username" in session:
        if request.method == 'POST':
            stuid = request.form.get('stuid')
            name = request.form.get('name')
            email = request.form.get('email')
            mbno = request.form.get('mbno')
            mtmarks = request.form.get('mtmarks')
            scmarks = request.form.get('scmarks')
            csmarks = request.form.get('csmarks')
            stu = Student.query.filter_by(stuid=stuid).first()
            stu.stuid = stuid
            stu.name = name
            stu.email = email
            stu.mbno = mbno
            stu.mtmarks = mtmarks
            stu.scmarks = scmarks
            stu.csmarks = csmarks
            db.session.add(stu)
            db.session.commit()
            return redirect("/admin")
        stu = Student.query.filter_by(stuid=stuid).first()
        return render_template('update.html',stu=stu)
    else:
        return redirect("/login")


@app.route("/delete/<int:stuid>")
def delete(stuid):
    if "username" in session:
        stu = Student.query.filter_by(stuid=stuid).first()
        db.session.delete(stu)
        db.session.commit()
        return redirect("/admin")
    else:
        return redirect("/login")
@app.route('/search', methods=["POST"] )
def search():
    if "username" in session:
        if request.method == 'POST':
            search = request.form.get('searched')
            searched = Student.query.all()
            return render_template('search.html', search=search, searched=searched)

if __name__ == "__main__":
    app.run(debug=True)