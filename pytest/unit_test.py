from math import e
from unittest.mock import patch
import pytest
from sqlalchemy import StaticPool, create_engine
from main import app, convert_month, create_share,  get_expense_data, get_expenses_by_cid_and_month, process_expense_data, validate_amount, validate_name, get_customer_by_cid, get_expenses_by_cid, get_expenses_by_cid_and_search, get_customer_by_email, get_share_by_joint_id_1, get_expense_by_id, create_expense, create_customer, delete_expense, update_customer, update_customer_budget, balance_update
from db import Base, db
from manage import populate_customers, populate_expenses, populate_shares
from models import Customers, Expenses, Shares
from sqlalchemy.orm import sessionmaker

'''
Build up testing database
'''


@pytest.fixture
def create_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    return app


@pytest.fixture
def setup_data(create_app):
    with create_app.app_context():
        db.drop_all()
        db.create_all()
        customer1 = Customers(cid=1, email="test@test.com",
                              password="password", first_name="first", last_name="last")
        customer2 = Customers(cid=2, email="test2@test.com",
                              password="password2", first_name="first2", last_name="last2")
        db.session.add(customer1)
        db.session.add(customer2)
        db.session.commit()

        for i in range(5):
            expense = Expenses(name=f"test{
                               i}", amount=i*100, date="2022-01-01", description=f"test description{i}", customer_id=1)
            db.session.add(expense)
        db.session.commit()

        share = Shares(sid=1, joint_id_1=1, joint_id_2=2)
        db.session.add(share)
        db.session.commit()

    yield

    with create_app.app_context():
        db.session.rollback()
        db.session.close()


def print_database_state(create_app):
    with create_app.app_context():

        customers = db.session.query(Customers).all()
        print("Customers:")
        for customer in customers:
            print(f"ID: {customer.cid}, Email: {customer.email}, First Name: {
                  customer.first_name}, Last Name: {customer.last_name}")

        expenses = db.session.query(Expenses).all()
        print("Expenses:")
        for expense in expenses:
            print(f"ID: {expense.eid}, Name: {expense.name}, Amount: {expense.amount}, Date: {
                  expense.date}, Description: {expense.description}, Customer ID: {expense.customer_id}")

        shares = db.session.query(Shares).all()
        print("Shares:")
        for share in shares:
            print(f"ID: {share.sid}, joint_id_1: {
                  share.joint_id_1}, joint_id_2: {share.joint_id_2}")


'''
Tests begin!!!
'''
'''
Test validation
'''


def test_validate_name(create_app):
    with create_app.app_context():
        assert validate_name("Valid Name") is True
        assert validate_name("") is False
        assert validate_name(None) is False
        assert validate_name(123) is False


def test_validate_amount(create_app):
    with create_app.app_context():
        assert validate_amount("123.45") == 123.45
        assert validate_amount("invalid") is None
        assert validate_amount(None) is None
        assert validate_amount("123") == 123.0


'''
Test the database is built up properly
'''


def test_customers_exist(create_app, setup_data):
    with create_app.app_context():
        customers = Customers.query.all()
        assert len(customers) == 2
        assert customers[0].email == "test@test.com"
        assert customers[1].email == "test2@test.com"


def test_expenses_exist(create_app, setup_data):
    with create_app.app_context():
        expenses = Expenses.query.filter_by(customer_id=1).all()
        assert len(expenses) == 5
        for i, expense in enumerate(expenses):
            assert expense.name == f"test{i}"
            assert expense.amount == i * 100
            assert expense.description == f"test description{i}"


def test_share_exists(create_app, setup_data):
    with create_app.app_context():
        share = Shares.query.first()
        assert share is not None
        assert share.joint_id_1 == 1
        assert share.joint_id_2 == 2


def test_customers_to_json(create_app, setup_data):
    with create_app.app_context():
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


def test_expenses_to_json(create_app, setup_data):
    with create_app.app_context():
        expense = db.session.query(Expenses).filter_by(eid=1).scalar()
        expense_json = expense.to_json()
        expected = {
            'id': 1,
            'name': 'test0',
            'amount': 0,
            'date': '2022-01-01',
            'description': 'test description0',
            'customer_id': 1
        }
        assert expense_json == expected


def test_shares_to_json(create_app, setup_data):
    with create_app.app_context():
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


def test_get_customer_by_cid(create_app, setup_data):
    with create_app.app_context():
        customer = get_customer_by_cid(1)
        assert isinstance(customer, Customers)
        assert customer.cid == 1


'''
Test get the correct expenses by cid=1
'''


def test_get_expenses_by_cid(create_app, setup_data):
    with create_app.app_context():
        expenses = get_expenses_by_cid(1)
        for expense in expenses:
            assert isinstance(expense[0], Expenses)
            assert expense[0].customer_id == 1


'''
Test get the correct customer by email
'''


def test_get_customer_by_email(create_app, setup_data):
    with create_app.app_context():
        customer = get_customer_by_email("test@test.com")
        assert isinstance(customer, Customers)
        assert customer.email == "test@test.com"


'''
Test get the correct share record by joint_id_1
'''


def test_get_share_by_joint_id_1(create_app, setup_data):
    with create_app.app_context():
        share = get_share_by_joint_id_1(1)
        assert isinstance(share, Shares)
        assert share.joint_id_1 == 1


'''
Test get the correct expense by eid
'''


def test_get_expense_by_id(create_app, setup_data):
    with create_app.app_context():
        print_database_state(create_app)
        expense = get_expense_by_id(1)
        assert isinstance(expense, Expenses)
        assert expense.eid == 1


'''
Test create an expense with correct name, amount and description
'''


def test_process_expense_data_single(create_app, setup_data):
    with create_app.app_context():
        data = {"eid": 6, "name": "test", "amount": 100, "date": "2022-01-01"}
        balance = 100

        expense = process_expense_data(data, balance)[0]

        assert expense["name"] == "test"
        assert expense["amount"] == 100
        assert expense["date"] == "2022-01-01"


def test_process_expense_data(create_app, setup_data):
    with create_app.app_context():
        data = db.session.execute(db.select(Expenses))
        balance = 100
        expense = process_expense_data(data, balance)
        expense.reverse()
        assert len(expense) == 5
        for i, e in enumerate(expense):
            print(i, e)
            assert e["name"] == f"test{i}"
            assert e["amount"] == i * 100
            assert e["date"] == "2022-01-01"


def test_create_expense(create_app, setup_data):
    with create_app.app_context():
        create_expense("test5", 100, "2022-01-01", "test description5", 1)
        expense = get_expense_by_id(6)
        assert expense.name == "test5"
        assert expense.amount == 100
        assert expense.date == "2022-01-01"
        assert expense.description == "test description5"
        assert expense.customer_id == 1


def test_create_customer(create_app, setup_data):
    with create_app.app_context():
        create_customer("test3@test.com", "password3", "first3", "last3")
        customer = get_customer_by_email("test3@test.com")
        assert customer.email == "test3@test.com"
        assert customer.password == "password3"
        assert customer.first_name == "first3"
        assert customer.last_name == "last3"


def test_delete_expense(create_app, setup_data):
    with create_app.app_context():
        create_expense("test", 100, "2022-01-01", "test description", 1)
        expense = get_expense_by_id(1)
        delete_expense(expense)
        with pytest.raises(Exception):
            get_expense_by_id(1)


def test_update_customer(create_app, setup_data):
    with create_app.app_context():
        customer = get_customer_by_cid(1)
        customer.first_name = "updated"
        update_customer(customer)
        updated_customer = get_customer_by_cid(1)
        assert updated_customer.first_name == "updated"


'''
Test Feature 2 -- get the correct expenses by cid=1 and search word
'''


def test_get_expenses_by_cid_and_search(create_app, setup_data):
    with create_app.app_context():
        expenses = get_expenses_by_cid_and_search(1, "test")
        for expense in expenses:
            assert isinstance(expense[0], Expenses)
            assert expense[0].customer_id == 1
            assert "test" in expense[0].name


def test_get_expense_data_under_search(create_app, setup_data):
    with create_app.app_context():
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
    with create_app.app_context():
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


def test_get_expenses_by_cid_and_month(create_app, setup_data):
    with create_app.app_context():
        expenses = get_expenses_by_cid_and_month(1, "01")
        for expense in expenses:
            # print(expense[0].date)
            assert isinstance(expense[0], Expenses)
            assert expense[0].customer_id == 1
            assert "2022-01" in expense[0].date


'''
Test Feature -- convert month
'''


def test_convert_month(create_app, setup_data):
    with create_app.app_context():
        month = 1
        result = convert_month(month)
        assert result == "01"
        month = 2
        result = convert_month(month)
        assert result == "02"
        month = 12
        assert convert_month(month) == "12"


'''
Test feature 1 -- update customer's budget
'''


def test_update_customer_budget(create_app):
    with create_app.app_context():
        customer1 = get_customer_by_cid(1)
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


def test_create_share(create_app, setup_data):
    with create_app.app_context():
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


# def test_get_budget_with_joint(create_app, setup_data):
#     with create_app.app_context():
#         customer1 = get_customer_by_cid(1)
#         customer2 = get_customer_by_cid(2)
#         customer1.joint = customer2.email
#         customer2.budget = 1000
#         result = get_budget(customer1)

#         assert result == 1000


# def test_get_budget_none(create_app, setup_data):
#     with create_app.app_context():
#         customer1 = get_customer_by_cid(1)
#         result = get_budget(customer1)
#         assert result == 0


# def test_get_budget_without_joint(create_app, setup_data):
#     with create_app.app_context():
#         customer1 = get_customer_by_cid(1)
#         customer2 = get_customer_by_cid(2)
#         customer1.budget = 500
#         customer1.joint = None
#         result = get_budget(customer1)
#         assert result == 500


'''test manage.py'''


def test_populate_expenses(create_app, setup_data):
    with create_app.app_context():
        Expenses.query.delete()
        db.session.commit()
        populate_expenses()
        expenses = Expenses.query.all()
        assert len(expenses) > 0


def test_populate_customers(create_app, setup_data):
    with create_app.app_context():
        Customers.query.delete()
        db.session.commit()
        populate_customers()
        customers = Customers.query.all()
        assert len(customers) > 0


def test_populate_shares(create_app, setup_data):
    with create_app.app_context():
        Shares.query.delete()
        db.session.commit()
        populate_shares()
        shares = Shares.query.all()
        assert len(shares) > 0


def test_balance_update(create_app):
    with create_app.app_context():
        cid = 1
        customer = get_customer_by_cid(cid)
        bal_data = get_expenses_by_cid(cid)
        balance = balance_update(customer.balance, bal_data)
        print(balance)
        assert balance[0] == -1000.0
