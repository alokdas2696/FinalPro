
import os

from flask import Flask, render_template, session, redirect, flash, make_response
from flask_sqlalchemy import SQLAlchemy, request
import random
from flask_mail import *
import pdfkit


app = Flask(__name__)
app.secret_key = "login"


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/studb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def generate_otp():
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


@app.route('/', methods=['GET'])
def home():
    session.pop('username', None)
    return render_template("email.html")


def send_otp(email, x):
    x = generate_otp()
    session['response'] = str(x)  # Storing otp in session
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('alokdas9626@gmail.com', 'keoqvilaqresvgvj')
        subject = 'OTP FROM RESULT SERVER'
        body = x
        msg = f'Subject:{subject}\n\nDear Student \n \n ' \
              f'The one-time password (OTP) for validating your email id is :-{body} ' \
              f'and do not share this OTP with anyone.'
        smtp.sendmail('alokdas9626@gmail,com', email, msg)


@app.route("/resendotp", methods=['GET', 'POST'])
def resend():
    if request.method == 'POST':
        if 'email' in session:
            emaildb = session['email'][0]
            x = generate_otp()  # generate otp
            send_otp(emaildb, x)  # resend otp
            d = session['email'][1]
            return render_template("verify.html", d=d)
    return redirect('/')


@app.route("/verify", methods=['GET','POST'])
def verify():
    if request.method == 'POST':
        d = request.form['rollno']
        stuid = Student.query.get(d)
        if stuid is None:
            return render_template('email.html', msg="Please Enter Valid Roll NO")

        emaildb = stuid.email
        session['email'] = (emaildb, d)    #will store this in session for resend otp
        x = generate_otp()
        send_otp(emaildb, x)

        return render_template("verify.html", d=d)
    return render_template("email.html")


@app.route('/validate/<int:d>', methods=['GET', 'POST'])
def validate(d):
    if request.method == 'POST':
        f = Student.query.get(d)
        emaildb = f.email
        userotp = request.form['otp']
        if 'response' in session:
            s = session['response']
            session.pop('response', None)
            if s == str(userotp):

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('alokdas9626@gmail.com', 'keoqvilaqresvgvj')
                    subject = 'Result'
                    body = (str(f.name) + "\n Email: " + str(f.email) + "\n Math Marks: " + str(f.mtmarks) +
                            "\n Science Marks: " + str(f.scmarks)+ "\n Computer Marks: " + str(f.csmarks) +
                            "\n Total Marks:" + str(f.csmarks + f.mtmarks + f.scmarks) + "\n Percenatge: " +
                            str(round(((f.csmarks + f.mtmarks + f.scmarks)/300)*100)))

                    msg = f'Subject:{subject}\n\n{body}'
                    smtp.sendmail('alokdas9626@gmail,com', emaildb, msg)
                return render_template('result.html', f=f, d=d,
                                       msg="Result has been Send to your given respected Email Id")
        return render_template("email.html", msg="Wrong OTP!........Please Login Again")
        # return render_template('email.html')


@app.route('/download/<int:d>',methods=['GET','POST'])
def download(d):
    f = Student.query.get(d)
    rendered = render_template('result.html', f=f, msg="Result has been Send to your given respected Email Id")
    path_wkthmltopdf = b"C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=MyResult.pdf'
    return response


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


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if "username" in session:
        page = request.args.get('page', 1, type=int)
        alldata1 = Student.query.order_by(Student.stuid.asc()).paginate(page=int(page), per_page=5)
        return render_template('index1.html', alldata1=alldata1)
    else:
        return redirect('/')


@app.route('/add', methods=['GET', 'POST'])
def addstu():
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

            stu = Student(stuid=stuid.strip(), name=name.strip(), email=email.strip(),
                          mbno=mbno.strip(), mtmarks=mtmarks.strip(), scmarks=scmarks.strip(),
                          csmarks=csmarks.strip())
            db.session.add(stu)
            db.session.commit()
            flash(f"Data inserted successfully ", "info")
            return redirect('/admin')
        return render_template('add.html')
    return redirect('/')


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
        return redirect("/")


@app.route("/delete/<int:stuid>")
def delete(stuid):
    if "username" in session:
        stu = Student.query.filter_by(stuid=stuid).first()
        db.session.delete(stu)
        db.session.commit()
        flash(f"Data deleted successfully ", "danger")
        return redirect("/admin")
    else:
        return redirect("/")


@app.route('/search',methods=['GET','POST'])
def search():
    if 'username' in session:
        if request.method == 'POST' and 'tag' in request.form:
            tag = request.form.get('tag')
            search = "%{}%".format(tag)
            page = request.args.get('page', 1, type=int)
            alldata1 = Student.query.filter(Student.name.like(search)).paginate(per_page=20, page=int(page))
            return render_template('index1.html', alldata1=alldata1, tag=tag)
        return render_template("email.html")
    return redirect('/')




if __name__ == "__main__":
    app.run(debug=True)