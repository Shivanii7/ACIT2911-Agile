from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from db import db


class Expenses(db.Model):
    eid = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    # NOTE put date instead of a string
    date = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False, default='N/A')
    customer_id = Column(Integer, ForeignKey("customers.cid",
                                             ondelete="CASCADE"), nullable=False)
    customer = relationship("Customers", back_populates="expenses")

    def to_json(self):
        return {
            'id': self.eid,
            'name': self.name,
            'amount': self.amount,
            'date': self.date,
            'customer_id': self.customer_id,
            'description': self.description
        }


class Customers(db.Model):
    cid = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    expenses = relationship("Expenses", back_populates="customer")

    def to_json(self):
        return {
            'id': self.cid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password': self.password
        }
