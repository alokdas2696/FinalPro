
import os

from flask import Flask, render_template, session,redirect,flash,make_response
from flask_sqlalchemy import SQLAlchemy, request
import random
import smtplib
from email.message import EmailMessage
from flask_mail import *
import json
import pdfkit
path_wkthmltopdf = b"C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)


# from random import randint
app = Flask(__name__)
app.secret_key = "login"


# with open('config.json', 'r') as k:
#     params = json.load(k)['params']
# otp = randint(1111, 9999)



app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/studb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = params['gmail-user']
# app.config['MAIL_PASSWORD'] = params['gmail-password']
# app.config['MAIL_USERNAME'] = ['gmail-user']
# app.config['MAIL_PASSWORD'] = ['gmail-password']
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


def generateOtp():
    return random.randint(1111, 9999)

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



def sendOtp(email, x):
    msg = EmailMessage()
    msg['Subject'] = 'OTP FROM Alok Server'
    msg['From'] = 'alokdas9626@gmail.com'
    msg['To'] = email
    # x = generateOtp()
    msg.set_content(str(x))
    session['response'] = str(x)  # Storing otp in session

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('alokdas9626@gmail.com','keoqvilaqresvgvj')
        smtp.send_message(msg)


@app.route('/', methods=['GET'])
def home():
    session.pop('username', None)
    return render_template("email.html")


# @app.route('/verify', methods=['GET', 'POST'])
# def verify():
#     if request.method == 'POST':
#         # email = request.form.get('email')
#
#         d = request.form.get('rollno')
#         stuid = Student.query.get(d)
#         if stuid == None:
#             return "Invalid Roll number ... go back"
#         email = stuid.email
#         # if email.strip() == email:
#
#
#         if email.strip() == email:
#             msg = Message('OTP',sender='alokdas9626@gmail.com', recipients=[email])
#             msg.body = str(otp)
#             mail.send(msg)
#             return render_template("verify.html", d=d)
#         else:
#             return " Unmatched EmailID with Roll No"
#     return render_template('verify.html')

@app.route("/verify", methods=['GET','POST'])
def verify():
    if request.method == 'POST':
        d = request.form['rollno']
        stuid = Student.query.get(d)
        if stuid is None:
            return render_template('email.html', msg="Please Enter Valid Roll NO")

        emaildb = stuid.email
        session['email'] = (emaildb, d)    #will store this in session for resend otp
        x = generateOtp()
        sendOtp(emaildb, x)

        return render_template("verify.html", d=d)
    return render_template("email.html")


@app.route("/resendotp", methods=['POST'])
def resend():
    if request.method == 'POST':
        if 'email' in session:  # resend otp
            emaildb = session['email'][0]  # resend otp
            x = generateOtp()  # resend otp
            sendOtp(emaildb, x)  # resend otp
            d = session['email'][1]
            return render_template("verify.html", d=d)
        return render_template("email.html")


@app.route('/validate/<int:d>',methods=['GET', 'POST'])
def validate(d):
    if request.method == 'POST':
        f = Student.query.get(d)
        emaildb = f.email
        userotp = request.form['otp']
        if 'response' in session:
            s = session['response']
            session.pop('response', None)
            if s == str(userotp):
                # if otp == int(userotp):
                msg = EmailMessage()
                msg['Subject'] = 'Mail from Alok server'
                msg['From'] = 'alokdas9626@gmail.com'
                msg['To'] = emaildb

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('alokdas9626@gmail.com', 'keoqvilaqresvgvj')
                    # subject = 'Res'
                    body = (str(f.name) + "\n Email: " + str(f.email) + "\n Math Marks: " + str(f.mtmarks) + "\n Science Marks: " + str(f.scmarks)+ "\n Computer Marks: " + str(f.csmarks)+ "\n Total Marks:" + str(f.csmarks + f.mtmarks + f.scmarks)+ "\n Percenatge: " + str(((f.csmarks + f.mtmarks + f.scmarks)/300)*100))

                    msg = f'{body}'
                    smtp.sendmail('alokdas9626@gmail,com', emaildb, msg)
                return render_template('result.html', f=f, d=d, msg="Result has been Send to your given respected Email Id")
        return render_template("email.html", msg="Otp not verified .... Wrong OTP!")
        # return render_template('email.html', msg="Session Expired (Otp Already Used) Try again !")


# @app.route('/validate/<int:d>',methods=['GET', 'POST'])
# def validate(d):
#     if request.method == 'POST':
#         f = Student.query.get(d)
#         gmail = f.email
#         userotp = request.form['otp']
#         if otp == int(userotp):
#             mail.send_message("Result: ",sender='alokdas9626@gmail.com', recipients=[gmail], body=f.name + "\n Email: " + f.email + "\n Math Marks: " + str(f.mtmarks)
#                               + "\n Science Marks: " + str(f.scmarks)+ "\n Computer Marks: " + str(f.csmarks)+ "\n Total Marks:"
#                             + str(f.csmarks + f.mtmarks + f.scmarks)+ "\n Percenatge: " +str(round(((f.csmarks + f.mtmarks + f.scmarks)/300)*100)))
#
#             return render_template('result.html',f=f, d=d, msg="Result has been Send to your given respected Email Id")
#         return render_template('email.html', msg="Not Verified !! try again")



@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username.strip() == "admin" and password.strip() == "12345":
            session['username'] = username
            return redirect("/admin")
        else:
            msg = " Invalid username/ password"
            return render_template("login.html", msg=msg)
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('username')
    return render_template('login.html')


@app.route("/admin", methods=['GET','POST'])
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
            flash(f"Data inserted successfully ", "info")

        page = request.args.get('page', 1, type=int)
        alldata1 = Student.query.order_by(Student.stuid.asc()).paginate(page=int(page), per_page=5)
        return render_template('index1.html', alldata1=alldata1)
    else:
        return redirect('/login')


@app.route("/update/<int:stuid>", methods=['GET', 'POST'])
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
            try:
                db.session.add(stu)
                db.session.commit()
            except Exception:
                db.session.rollback()
                flash(f"This email already exits", "info")
                return redirect('/admin')
            flash(f"Data updated successfully ", "info")
            return redirect("/admin")

        stu = Student.query.filter_by(stuid=stuid).first()
        return render_template('update.html', stu=stu)
    else:
        return redirect("/login")


@app.route("/delete/<int:stuid>")
def delete(stuid):
    if "username" in session:
        stu = Student.query.filter_by(stuid=stuid).first()
        db.session.delete(stu)
        db.session.commit()
        flash(f"Data deleted successfully ", "danger")
        return redirect("/admin")
    else:
        return redirect("/login")

@app.route('/search',methods=['GET','POST'])
def search():
    if 'username' in session:
        if request.method == 'POST' and 'tag' in request.form:
            tag = request.form.get('tag')
            search = "%{}%".format(tag)
            page = request.args.get('page', 1, type=int)
            alldata1 = Student.query.filter(Student.name.like(search)).paginate(per_page=20, page=int(page))
            return render_template('index1.html', alldata1=alldata1, tag=tag)

        return render_template("login.html")


@app.route('/download/<int:d>')
def download(d):
    f = Student.query.get(d)
    rendered = render_template('result.html', f=f, msg="Result has been Send to your given respected Email Id")
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=MyResult.pdf'
    return response


if __name__ == "__main__":
    app.run(debug=True)