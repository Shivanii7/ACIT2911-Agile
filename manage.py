from main import create_app
from db import db
from models import Expenses, Customers, Shares
from csv import DictReader


app = create_app()


def populate_expenses():
    with app.app_context():
        with open('./data/expenses.csv', 'r') as file:
            # csv methods to read the file
            reader = DictReader(file)
            expenses = list(reader)
            for row in expenses:
                date_str = row['date']
                expense = Expenses(
                    name=row['items'], amount=row['expense'], date=date_str, customer_id=row['cid'])
                db.session.add(expense)
            db.session.commit()


def populate_customers():
    with app.app_context():
        with open('./data/customers.csv', 'r') as file:
            reader = DictReader(file)
            customers = list(reader)
            for row in customers:
                customer = Customers(
                    email=row['email'], first_name=row['first_name'], last_name=row['last_name'], password=row['password'], balance=row['balance'], budget=row['budget'], joint=row['joint'], spent=row['spent'])
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


with app.app_context():
    db.drop_all()
    db.create_all()
    populate_expenses()
    populate_customers()
    populate_shares()
