# import sys
# sys.path.insert(
#     0, "C:/Users/sarah/OneDrive/miniTerm/ACIT2911/ACIT2911-Agile/production")
from datetime import datetime
import pytest
from io import BytesIO
from unittest.mock import mock_open, patch
from db import db
from manage import populate_customers, populate_expenses, populate_shares
from models import Customers, Expenses, Shares
from werkzeug.datastructures import FileStorage
from main import convert_month, create_app, create_share, get_current_month_spent,  get_expense_data, get_expenses_by_cid_and_month, get_transaction_by_id, process_expense_data, update_balance, update_current_month_spent, update_spent, update_transaction, validate_amount, validate_name, get_customer_by_cid, get_expenses_by_cid, get_expenses_by_cid_and_search, get_customer_by_email, get_share_by_joint_id_1, get_expense_by_id, create_expense, create_customer, delete_expense, update_customer, update_customer_budget, balance_update, update_current_month_spent_expense

'''
Build up testing database
'''

@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.rollback()


# @pytest.fixture
# def client(app):
#     return app.test_client()


@pytest.fixture
def setup_data(app):
    # with client:
    with app.app_context():
        customer1 = Customers(cid=1, email="test@test.com",
                                password="password", first_name="first", last_name="last")
        customer2 = Customers(cid=2, email="test2@test.com",
                                password="password2", first_name="first2", last_name="last2")
        db.session.add(customer1)
        db.session.add(customer2)
        db.session.commit()

        for i in range(5):
            expense = Expenses(name=f"test{i}", amount=i*100, date="2022-01-01", customer_id=1, transaction_category="expense", receipt_image_path="test0.jpg")
            db.session.add(expense)
        for i in range(5,10,1):
            expense = Expenses(name=f"test{i}", amount=i*100, date="2022-01-01", customer_id=1, transaction_category="income", receipt_image_path="test1.jpg")
            db.session.add(expense)
        db.session.commit()

        share = Shares(sid=1, joint_id_1=1, joint_id_2=2)
        db.session.add(share)
        db.session.commit()

    # return client


def print_database_state(app):
    with app.app_context():

        customers = db.session.query(Customers).all()
        print("Customers:")
        for customer in customers:
            print(f"ID: {customer.cid}, Email: {customer.email}, First Name: {customer.first_name}, Last Name: {customer.last_name}")

        expenses = db.session.query(Expenses).all()
        print("Expenses:")
        for expense in expenses:
            print(f"ID: {expense.eid}, Name: {expense.name}, Amount: {expense.amount}, Date: {expense.date}, Customer ID: {expense.customer_id}, Transaction Category: {expense.transaction_category}, Receipt Image Path: {expense.receipt_image_path}")

        shares = db.session.query(Shares).all()
        print("Shares:")
        for share in shares:
            print(f"ID: {share.sid}, joint_id_1: {share.joint_id_1}, joint_id_2: {share.joint_id_2}")


'''
Tests begin!!!
'''
'''
Test validation
'''


def test_validate_name(app):
    with app.app_context():
        assert validate_name("Valid Name") is True
        assert validate_name("") is False
        assert validate_name(None) is False
        assert validate_name(123) is False


def test_validate_amount(app):
    with app.app_context():
        assert validate_amount("123.45") == 123.45
        assert validate_amount("invalid") is None
        assert validate_amount(None) is None
        assert validate_amount("123") == 123.0


'''
Test the database is built up properly
'''


def test_customers_exist(app, setup_data):
    with app.app_context():
        customers = Customers.query.all()
        assert len(customers) == 2
        assert customers[0].email == "test@test.com"
        assert customers[1].email == "test2@test.com"


def test_expenses_exist(app, setup_data):
    with app.app_context():
        expenses = Expenses.query.filter_by(customer_id=1).all()
        assert len(expenses) == 10
        for i, expense in enumerate(expenses):
            assert expense.name == f"test{i}"
            assert expense.amount == i * 100
           


def test_share_exists(app, setup_data):
    with app.app_context():
        share = Shares.query.first()
        assert share is not None
        assert share.joint_id_1 == 1
        assert share.joint_id_2 == 2


def test_customers_to_json(app, setup_data):
    with app.app_context():
        customer = db.session.query(Customers).filter_by(cid=1).scalar()
        customer_json = customer.to_json()
        expected = {
            'id': 1,
            'email': 'test@test.com',
            'first_name': 'first',
            'last_name': 'last',
            'password': 'password',
            'balance': 0,
            'budget': 0,
            'joint': None,
            'spent': 0
        }
        assert customer_json == expected


def test_expenses_to_json(app, setup_data):
    with app.app_context():
        expense = db.session.query(Expenses).filter_by(eid=1).scalar()
        expense_json = expense.to_json()
        expected = {
            'id': 1,
            'name': 'test0',
            'amount': 0,
            'date': '2022-01-01',
            'transaction_category': 'expense',
            # 'description': 'test description0',
            'customer_id': 1,
            'receipt_image_path': "test0.jpg"
        }
        assert expense_json == expected


def test_shares_to_json(app, setup_data):
    with app.app_context():
        share = db.session.query(Shares).filter_by(sid=1).scalar()
        share_json = share.to_json()
        expected = {
            'id': 1,
            'item': 'budget',
            'joint_id_1': 1,
            'joint_id_2': 2
        }
        assert share_json == expected


'''
Test the correct customer by cid=1
'''


def test_get_customer_by_cid(app, setup_data):
    with app.app_context():
        customer = get_customer_by_cid(1)
        assert isinstance(customer, Customers)
        assert customer.cid == 1

def test_get_transaction_by_id(app,setup_data):
    with app.app_context():
        transaction = get_transaction_by_id(1)
        assert isinstance(transaction, Expenses)
        assert transaction.eid == 1

def test_pdate_transaction(app,setup_data):
    with app.app_context():
        result = update_transaction(6, "apple", "2024-05-10", 100, "expense")
        assert result is None
        transaction = get_transaction_by_id(1)
        update_transaction(1,"apple","2024-05-10",100,"expense")
        assert transaction.name=="apple"        
        assert transaction.date == "2024-05-10"
        assert transaction.amount == 100
        assert transaction.transaction_category == "expense"



'''
Test get the correct expenses by cid=1
'''


def test_get_expenses_by_cid(app, setup_data):
    with app.app_context():
        expenses = get_expenses_by_cid(1)
        for expense in expenses:
            assert isinstance(expense[0], Expenses)
            assert expense[0].customer_id == 1


'''
Test get the correct customer by email
'''


def test_get_customer_by_email(app, setup_data):
    with app.app_context():
        customer = get_customer_by_email("test@test.com")
        assert isinstance(customer, Customers)
        assert customer.email == "test@test.com"


'''
Test get the correct share record by joint_id_1
'''


def test_get_share_by_joint_id_1(app, setup_data):
    with app.app_context():
        share = get_share_by_joint_id_1(1)
        assert isinstance(share, Shares)
        assert share.joint_id_1 == 1


'''
Test get the correct expense by eid
'''


def test_get_expense_by_id(app, setup_data):
    with app.app_context():
        print_database_state(app)
        expense = get_expense_by_id(1)
        assert isinstance(expense, Expenses)
        assert expense.eid == 1


'''
Test create an expense with correct name, amount and description
'''


def test_process_expense_data_single(app, setup_data):
    with app.app_context():
        data = {"eid": 6, "name": "test", "amount": 100, "date": "2022-01-01", "transaction_category": "expense", "receipt_image_path": "test0.jpg"}
        balance = 100

        expense = process_expense_data(data, balance)[0]

        assert expense["name"] == "test"
        assert expense["amount"] == 100
        assert expense["date"] == "2022-01-01"
        assert expense["transaction_category"] == "expense"
        assert expense["receipt_image_path"] == "test0.jpg"
        
def test_process_expense_data_income_single(app, setup_data):
    with app.app_context():
        data = {"eid": 6, "name": "test", "amount": 100, "date": "2022-01-01", "transaction_category": "income", "receipt_image_path": "test0.jpg"}
        balance = 100        
        expense = process_expense_data(data, balance)
        expense.reverse()
        assert len(expense) == 1
        for i, e in enumerate(expense):
            print(i, e)
            assert e["name"] == "test"
            assert e["amount"] == i + 100
            assert e["date"] == "2022-01-01" 
            assert e["transaction_category"] == "income"
            assert e["receipt_image_path"] == "test0.jpg" 


def test_process_expense_data(app, setup_data):
    with app.app_context():
        data = db.session.execute(db.select(Expenses).where(Expenses.transaction_category == "expense"))
        balance = 100
        expense = process_expense_data(data, balance)
        expense.reverse()
        assert len(expense) == 5
        for i, e in enumerate(expense):
            print(i, e)
            assert e["name"] == f"test{i}"
            assert e["amount"] == i * 100
            assert e["date"] == "2022-01-01"
            assert e["transaction_category"] == "expense"
            

def test_process_expense_data_income(app, setup_data):
    print_database_state(app)
    with app.app_context():
        data = db.session.execute(db.select(Expenses).where(Expenses.transaction_category == "income"))
        balance = 100
        expense = process_expense_data(data, balance)
        expense.reverse()
        assert len(expense) == 5
        for i, e in enumerate(expense):
            print(i, e)
            assert e["name"] == f"test{i+5}"
            assert e["amount"] == (i+5) * 100
            assert e["date"] == "2022-01-01"
            assert e["transaction_category"] == "income"

def test_create_expense(app, setup_data):
    with app.app_context():
        receipt_image_data = (BytesIO(b"dummy image data"), 'test0.jpg')
        receipt_image_file = FileStorage(receipt_image_data[0], filename=receipt_image_data[1])
        create_expense("test11", 100, "2022-01-01", "expense", 1, receipt_image_file)
        expense = get_expense_by_id(11)
        assert expense.name == "test11"
        assert expense.amount == 100
        assert expense.date == "2022-01-01"
        assert expense.customer_id == 1
        assert expense.transaction_category == "expense"
        assert "test0.jpg" in expense.receipt_image_path

def test_create_customer(app, setup_data):
    with app.app_context():
        create_customer("test3@test.com", "password3", "first3", "last3")
        customer = get_customer_by_email("test3@test.com")
        assert customer.email == "test3@test.com"
        assert customer.password == "password3"
        assert customer.first_name == "first3"
        assert customer.last_name == "last3"


def test_delete_expense(app, setup_data):
    with app.app_context():
        create_expense("test", 100, "2022-01-01", "expense", 1)
        expense = get_expense_by_id(1)
        delete_expense(expense)
        with pytest.raises(Exception):
            get_expense_by_id(1)


def test_update_customer(app, setup_data):
    with app.app_context():
        customer = get_customer_by_cid(1)
        customer.first_name = "updated"
        update_customer(customer)
        updated_customer = get_customer_by_cid(1)
        assert updated_customer.first_name == "updated"
        
def test_update_spent(app, setup_data):
    with app.app_context():
        customer = get_customer_by_cid(1)
        update_spent(customer, 200)
        assert customer.budget == 0
        assert customer.balance == 0
        


'''
Test Feature 2 -- get the correct expenses by cid=1 and search word
'''


def test_get_expenses_by_cid_and_search(app, setup_data):
    with app.app_context():
        expenses = get_expenses_by_cid_and_search(1, "test")
        for expense in expenses:
            assert isinstance(expense[0], Expenses)
            assert expense[0].customer_id == 1
            assert "test" in expense[0].name


def test_get_expense_data_under_search(app, setup_data):
    with app.app_context():
        cid = 1
        search = None
        expenses = get_expenses_by_cid(cid)
        expense_list = []
        for expense in expenses:
            expense_list.append(expense[0])
        results = get_expense_data(cid, search)
        result_list = []
        for result in results:
            result_list.append(result)

        assert len(result_list) == len(expense_list)
        assert result_list[0][0] == expense_list[0]
    with app.app_context():
        cid = 1
        search = "1"
        expenses = get_expenses_by_cid_and_search(cid, search)
        expense_list = []
        for expense in expenses:
            expense_list.append(expense[0])
        results = get_expense_data(cid, search)
        result_list = []
        for result in results:
            result_list.append(result)

        assert len(result_list) == len(expense_list)
        assert result_list[0][0] == expense_list[0]



'''
Test Feature -- get the correct expenses by cid=1 and month
'''


def test_get_expenses_by_cid_and_month(app, setup_data):
    with app.app_context():
        expenses = get_expenses_by_cid_and_month(1, "01")
        for expense in expenses:
            # print(expense[0].date)
            assert isinstance(expense[0], Expenses)
            assert expense[0].customer_id == 1
            assert "2022-01" in expense[0].date


'''
Test Feature -- get current month expenses
'''

def test_get_current_month_spent(app,setup_data):
    with app.app_context():
        get_current_month_spent(1)
        customer = get_customer_by_cid(1)
        assert customer.budget == 0

def test_update_current_amount_spent(app, setup_data):
    with app.app_context():
        x = update_current_month_spent(1, '01')
        print(x)
        customer = get_customer_by_cid(1)
        assert customer.budget == 0
        assert customer.balance == 0
        
def test_update_current_amount_spent_expense(app, setup_data):
    with app.app_context():
        x = update_current_month_spent_expense(1, '01' )
        print(x)
        customer = get_customer_by_cid(1)
        assert customer.budget == 0
        assert customer.balance == 0


'''
Test Feature -- update balance
'''

def test_update_balance(app, setup_data):
    with app.app_context():
        update_balance(1, 100)
        assert get_customer_by_cid(1).balance == 0

'''
Test Feature -- convert month
'''


def test_convert_month(app, setup_data):
    with app.app_context():
        month = 1
        result = convert_month(month)
        assert result == "01"
        month = 2
        result = convert_month(month)
        assert result == "02"
        month = 12
        assert convert_month(month) == "12"

'''
Test feature -- update transaction fail
'''

def test_update_transactions(app, setup_data):
    with app.app_context():
        expense = update_transaction(12, "test", "2022-01-01", 100, "expense")
        assert expense == None

'''
Test feature 1 -- update customer's budget
'''


def test_update_customer_budget(app, setup_data):
    with app.app_context():
        customer1 = get_customer_by_cid(1)
        print(customer1.to_json())
        update_customer_budget(customer1, 200, 100)
        assert customer1.budget == 200
        assert customer1.balance == 100
        customer2 = get_customer_by_cid(2)
        update_customer_budget(customer1, 200, 100, customer2.email)
        assert customer1.budget == customer2.budget
        assert customer1.balance == 100
        update_customer_budget(customer1, 200, 100)
        assert customer1.budget == 200
        assert customer1.balance == 100


def test_create_share(app, setup_data):
    with app.app_context():
        customer = get_customer_by_cid(1)
        joint_customer = get_customer_by_cid(2)
        create_share(customer, joint_customer)

        share = Shares.query.filter_by(joint_id_1=1).first()
        assert share
        assert share.joint_id_2 == 2
        assert customer.budget == joint_customer.budget

        customer = get_customer_by_cid(1)
        joint_customer = None
        create_share(customer, joint_customer)
        assert customer.budget == customer.budget


def test_balance_update(app, setup_data):
    with app.app_context():
        cid = 1
        customer = get_customer_by_cid(cid)
        bal_data = get_expenses_by_cid(cid)
        balance = balance_update(customer.balance, bal_data)
        print(balance)
        assert balance[0] == 2500

'''test manage.py'''


@patch('manage.open', new_callable=mock_open, read_data='items,expense,date,cid,transaction_category,receipt_image_path\nitem1,100,2022-01-01,1,expense\nitem2,200,2022-01-02,2,expense,path2')
@patch('manage.db.session.commit')
@patch('manage.db.session.add')
def test_populate_expenses(mock_db_add, mock_db_commit, mock_file):
    populate_expenses()
    assert mock_db_add.call_count == 2
    mock_db_commit.assert_called_once()


@patch('manage.open', new_callable=mock_open, read_data='email,first_name,last_name,password,balance,budget,joint,spent\nnick123@gmail.com,Nick,Smith,nick123!,1000,500,N/A,0\nsarah123@gmail.com,Sarah,Brown,sarah123!,2000,800,N/A,0')
@patch('manage.db.session.commit')
@patch('manage.db.session.add')
def test_populate_customers(mock_db_add, mock_db_commit, mock_file):
    populate_customers()
    assert mock_db_add.call_count == 2
    mock_db_commit.assert_called_once()


@patch('manage.open', new_callable=mock_open, read_data='item,joint_id_1,joint_id_2\nbudget,1,2')
@patch('manage.db.session.commit')
@patch('manage.db.session.add')
def test_populate_shares(mock_db_add, mock_db_commit, mock_file):
    populate_shares()
    mock_db_add.assert_called_once()
    mock_db_commit.assert_called_once()
