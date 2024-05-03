from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import mapped_column
from db import db


class Expenses(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(String(255), nullable=False) #NOTE put date instead of a string 
    description = Column(String(255), nullable=False, default='N/A')
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'date': self.date,
            'description': self.description
        }