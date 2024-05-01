from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import mapped_column
from db import db


class Expenses(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    category = Column(String(255), nullable=False)
    date = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'category': self.category,
            'date': self.date,
            'description': self.description
        }