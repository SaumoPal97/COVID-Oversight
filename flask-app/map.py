from flask import Flask, render_template, url_for, request, redirect, jsonify, Response, session
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
from flask_marshmallow import Marshmallow
from trial import twilio_sms
from authy.api import AuthyApiClient

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']
api = AuthyApiClient(app.config['AUTHY_API_KEY'])

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    timeslot = db.Column(db.String(20), nullable=False)
    token = db.Column(db.String(200), nullable=False)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Integer, default=100)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)

class CaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Case

@app.route('/', methods=['POST', 'GET'])
def map_func():
    if request.method == 'POST':
        twilio_sms("Someone near you seems to need your help. Talk to them via +14243637976")
        return redirect('/')
    else:
        cases = Case.query.all()
        case_schema = CaseSchema(many=True)
        output = case_schema.dump(cases)
        return render_template('home.html', apikey='pK5yH0jJ-ZpsIokaaLFkOJuv8sv1QASAIOc-Isrn86E', cases=output)

@app.route('/cases', methods=['POST', 'GET'])
def case_func():
    if request.method == 'POST':
        twilio_sms("A new case was discovered near you")
        caseLatitude = request.form['latitude']
        caseLongtitude = request.form['longitude']
        caseRadius = request.form['radius']
        new_case = Case(latitude=caseLatitude, longitude=caseLongtitude, radius=caseRadius)
        try:
            db.session.add(new_case)
            db.session.commit()
            return redirect('/phone_verification')
        except:
            return 'There was an issue adding your case'
    else:
        cases = Case.query.order_by(Case.time_created.desc()).all()
        cases_all = Case.query.all()
        case_schema = CaseSchema(many=True)
        output = case_schema.dump(cases_all)
        return render_template('analysis.html', apikey='pK5yH0jJ-ZpsIokaaLFkOJuv8sv1QASAIOc-Isrn86E', cases=cases, heatmap=output)

@app.route('/bookings', methods=['POST','GET'])
def book_func():
    if request.method == 'POST':
        bookDate = str(request.form['date'])
        bookTimeSlot =  str(request.form['time'])
        bookToken = str(uuid.uuid1())
        twilio_sms("Your unique token is {}".format(bookToken))
        newBooking = Ticket(date=bookDate, timeslot = bookTimeSlot, token=bookToken)
        try:
            db.session.add(newBooking)
            db.session.commit()
            tickets = Ticket.query.order_by(Ticket.time_created.desc()).all()
            return render_template('ticket.html', tickets=tickets)
        except:
            return 'There was an issue creating your ticket'
    else:
        cases_all = Case.query.all()
        case_schema = CaseSchema(many=True)
        output = case_schema.dump(cases_all)
        return render_template('booking.html', apikey='pK5yH0jJ-ZpsIokaaLFkOJuv8sv1QASAIOc-Isrn86E', cases=output)

@app.route('/tickets')
def ticket_func():
    tickets = Ticket.query.order_by(Ticket.time_created.desc()).all()
    return render_template('ticket.html', tickets=tickets)

@app.route("/phone_verification", methods=["GET", "POST"])
def phone_verification():
    if request.method == "POST":
        country_code = request.form.get("country_code")
        phone_number = request.form.get("phone_number")
        method = request.form.get("method")

        session['country_code'] = country_code
        session['phone_number'] = phone_number

        api.phones.verification_start(phone_number, country_code, via=method)

        return redirect("/verify")

    return render_template("phone_verification.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        token = request.form.get("token")
        phone_number = session.get("phone_number")
        country_code = session.get("country_code")
        verification = api.phones.verification_check(phone_number, country_code, token)
        
        if verification.ok():
            return redirect('/cases')
    
    return render_template("verify.html")

if __name__=='__main__':
    app.run(debug=True)