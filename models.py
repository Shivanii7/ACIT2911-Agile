from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime
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
    shares_1 = relationship("Shares", foreign_keys="Shares.joint_id_1")
    shares_2 = relationship("Shares", foreign_keys="Shares.joint_id_2")
    balance = Column(Float, default=0)
    budget = Column(Float, default=0)
    joint = Column(String(255), default=None)

    def to_json(self):
        return {
            'id': self.cid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password': self.password,
            'balance': self.balance,
            'budget': self.budget,
            'joint': self.joint

        }


class Shares(db.Model):
    sid = Column(Integer, primary_key=True)
    item = Column(String(255), nullable=False, default="budget")

    joint_id_1 = Column(Integer, ForeignKey(
        "customers.cid", ondelete="CASCADE"), nullable=False)
    joint_id_2 = Column(Integer, ForeignKey(
        "customers.cid", ondelete="CASCADE"), nullable=False)
    customer_1 = relationship(
        "Customers", back_populates="shares_1", foreign_keys=[joint_id_1])
    customer_2 = relationship(
        "Customers", back_populates="shares_2", foreign_keys=[joint_id_2])

    def to_json(self):
        return {
            'id': self.sid,
            'item': self.item,
            'joint_id_1': self.joint_id_1,
            'joint_id_2': self.joint_id_2
        }
