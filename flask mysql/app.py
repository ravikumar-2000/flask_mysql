from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from email.message import EmailMessage
import smtplib
import os

import pymysql
from werkzeug.utils import redirect
pymysql.install_as_MySQLdb()
  
EMAIL = os.environ.get('MY_EMAIL')
PASS = os.environ.get('MY_EMAIL_PASS')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{os.environ.get('MYSQL_PASS')}@localhost/flaskExp'
# intitializing the database
db = SQLAlchemy(app)


# create database model
class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(50), nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    email = db.Column(db.String(30), nullable = False, unique = True)

    def __repr__(self):
        return '<Name %r>' % self.id

@app.route('/')
@app.route('/home')
def home():
    title = "Ravi Pande's Profile"
    return render_template('index.html', title = title)

@app.route('/about')
def about():
    names = ['ravi', 'hiten', 'jiten', 'vinayak sir', 'aman', 'sahil']
    title = 'ravi pande'
    return render_template('about.html', names = names, title = title)

@app.route('/subscribe')
def subscribe():
    title = 'subscribe'
    return render_template('subscribe.html', title = title)

@app.route('/form', methods=['POST', 'GET'])
def form():

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email_address = request.form.get('email_address')
        password = request.form.get('password')

        fields = [first_name, last_name, email_address, password]
        if not all(fields):
            error_statement = 'All fileds are mandatory to fill ....'
            return render_template('subscribe.html', error_statement = error_statement)
        else:
            try:
                new_subscriber = Subscribers(name = first_name + ' ' + last_name, email = email_address)
                db.session.add(new_subscriber)
                db.session.commit()

                msg = EmailMessage()
                msg['Subject'] = 'This is to inform you about your account setup!'
                msg['From'] = EMAIL
                msg['To'] = email_address
                msg.set_content(f'You have successfully signed up as {first_name} {last_name}.')
                # msg.set_content(f'Mr. {first_name} {last_name} {EMAIL} is trying to access your gamil account! If you are not this click here...\nhttps://www.ullubangaya.com')

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(EMAIL, PASS)
                    smtp.send_message(msg)
                    print(f'message sent to {email_address}')

                print(first_name, last_name, email_address, password)

                subscribers = Subscribers.query.order_by(Subscribers.date_created.desc())
                title = 'form-submission'
                return render_template('form.html', title = title, subscribers = subscribers)
            except:
                return 'there was an error!'
    else:
        subscribers = Subscribers.query.order_by(Subscribers.date_created.desc())
        return render_template('form.html', subscribers = subscribers)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    subscriber_id = Subscribers.query.get_or_404(id)
    if request.method == 'POST':
        subscriber_name = request.form.get('first_name') + ' ' + request.form.get('last_name')
        subscriber_email = request.form.get('email_address')
        subscriber_id.name = subscriber_name
        subscriber_id.email = subscriber_email
        try:
            db.session.commit()
            print('data altered successfully')
            subscribers = Subscribers.query.order_by(Subscribers.date_created.desc())
            return render_template('form.html', subscribers = subscribers)
        except:
            return 'there was an error'
    else:
        return render_template('update.html', subscriber = subscriber_id)

@app.route('/delete/<int:id>')
def delete(id):
    subscriber_id = Subscribers.query.get_or_404(id)
    try:
        db.session.delete(subscriber_id)
        db.session.commit()
        return redirect('/form')
    except:
        return 'there was an error'

if __name__ == '__main__':
    app.run(debug = True) 