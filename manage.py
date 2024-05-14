from main import app
from db import db
from models import Expenses, Customers, Shares
from csv import DictReader
from datetime import datetime


def populate_expenses():
    with app.app_context():
        with open('./data/expenses.csv', 'r') as file:
            # csv methods to read the file
            reader = DictReader(file)
            expenses = list(reader)
            for row in expenses:
                # print(row)
                date_str = row['date']
                date_obj = datetime.strptime(date_str, '%Y-%M-%d')
                date = date_obj.strftime('%B %d, %Y')
                expense = Expenses(
                    name=row['items'], amount=row['expense'], date=date, customer_id=row['cid'])
                # print(expense.to_json())
                db.session.add(expense)
            db.session.commit()


def populate_customers():
    with app.app_context():
        with open('./data/customers.csv', 'r') as file:
            reader = DictReader(file)
            customers = list(reader)
            for row in customers:
                customer = Customers(
                    email=row['email'], first_name=row['first_name'], last_name=row['last_name'], password=row['password'], balance=row['balance'], budget=row['budget'], joint=row['joint'])
                db.session.add(customer)
            db.session.commit()


def populate_shares():
    with app.app_context():
        with open('./data/shares.csv', 'r') as file:
            reader = DictReader(file)
            shares = list(reader)
            for row in shares:
                share = Shares(
                    item=row['item'], joint_id_1=row['joint_id_1'], joint_id_2=row['joint_id_2'])
                db.session.add(share)
            db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_expenses()
        populate_customers()
        populate_shares()
