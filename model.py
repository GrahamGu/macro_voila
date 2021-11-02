# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 16:42:17 2021

@author: jsomas_bigriv
"""


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Model(db.Model):
    __tablename__ = 'ebitda_variance'

    id = db.Column(db.Integer, primary_key=True)
    TargetEBITDA = db.Column(db.Integer())
    ThresholdEBITDA = db.Column(db.Integer())
    Variable = db.Column(db.Integer())
    Days = db.Column(db.Integer())
    Hrs = db.Column(db.Integer())
    Yield = db.Column(db.Float())
    Year = db.Column (db.Integer())
    Month = db.Column(db.String())
    EBITDA_Target = db.Column(db.Float())
    EBITDA_Thresh = db.Column(db.Float())
    DateTimeUpdated = db.Column(db.String())
    Username = db.Column(db.String())
    def __init__(self,TargetEBITDA, ThresholdEBITDA, Variable, Days, Hrs, Yield, Year, Month, EBITDA_Target, EBITDA_Thresh, DateTimeUpdated, Username):
        self.TargetEBITDA = TargetEBITDA
        self.ThresholdEBITDA = ThresholdEBITDA
        self.Variable = Variable
        self.Days = Days
        self.Hrs = Hrs
        self.Yield = Yield
        self.Year = Year
        self.Month = Month
        self.EBITDA_Target = EBITDA_Target
        self.EBITDA_Thresh = EBITDA_Thresh
        self.DateTimeUpdated = DateTimeUpdated
        self.Username = Username

    def __repr__(self):
        return f"<EBITDA {self.TargetEBITDA}:self.ThresholdEBITDA>"
    
    

    