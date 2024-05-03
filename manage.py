from main import app
from db import db
from models import Expenses
from csv import DictReader

def populate_expenses():
    with app.app_context():
        with open('./data/expenses.csv', 'r') as file:
            # csv methods to read the file
            reader = DictReader(file)
            expenses = list(reader)
            for row in expenses:
                expense = Expenses(name=row['items'], amount=row['expense'], date=row['date'])
                db.session.add(expense)
            db.session.commit() 
            
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_expenses()