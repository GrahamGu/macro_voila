# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 11:57:55 2021

@author: jsomas_bigriv
"""

from flask import Flask,render_template,request, redirect, url_for
from flask_migrate import Migrate
from model import db, Model
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://dwadmin:brsanalytics@40.113.234.203:5432/ui_throughput"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)


TargetEBITDA = ThresholdEBITDA = Variable = Days = Hrs = Year = 0
Month = Username = ""
Yield = EBITDA_Target = EBITDA_Thresh  = 0.0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    global Username
    
    if request.method == 'POST':
        Username = request.form['Username']
        return render_template('login.html')
    return render_template('index.html')
                   
    
    
@app.route('/form', methods = ['POST', 'GET'])
def insert():
   
    global TargetEBITDA, ThresholdEBITDA, Variable, Days, Hrs, Yield, Year, Month, EBITDA_Target, EBITDA_Thresh, Username
    
    
    if request.method == 'POST':
        TargetEBITDA = int(request.form['TargetEBITDA'])
        ThresholdEBITDA = int(request.form['ThresholdEBITDA'])
        Variable = int(request.form['Variable'])
        Days = int(request.form['Days'])
        Hrs = int(request.form['Hrs'])
        Yield = float(request.form['Yield'])
        Year = int(request.form['Year'])
        Month = request.form['Month']
        EBITDA_Target = ((TargetEBITDA*Days)+Variable)/(Days*Hrs*Yield*60)
        EBITDA_Thresh = ((ThresholdEBITDA*Days)+Variable)/(Days*Hrs*Yield*60)
        now = datetime.now()
        
        Format = "%m/%d/%Y %H:%M:%S"
        DateTimeUpdated = now.strftime(Format)
        new_record = Model(TargetEBITDA=TargetEBITDA, ThresholdEBITDA=ThresholdEBITDA, Variable=Variable, Days = Days,Hrs=Hrs,Yield = Yield,Year =  Year, Month = Month, EBITDA_Target= EBITDA_Target, EBITDA_Thresh = EBITDA_Thresh, DateTimeUpdated = DateTimeUpdated, Username = Username)
        db.session.add(new_record)
        db.session.commit()
        return render_template('form.html', pred_result = f"EBITDA Target is {EBITDA_Target} and EBITDA Threshold is {EBITDA_Thresh}")
        
        
    return render_template('login.html')
    



if __name__ == '__main__':
    app.run(debug=True)

