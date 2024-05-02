from main import app
from db import db
from models import Expenses

def populate_expenses():
    with app.app_context():
        ### open file
        ### read file
        ### loop through file
        ### create enpenses
        ### commit to database
        pass
    
if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    populate_expenses()
    app.run(debug=True, port=3000)