from unittest.mock import patch
import pytest
from flask import url_for
from flask_testing import TestCase
from main import app, create_share, get_budget, get_expense_data, process_expense_data
from db import db
from manage import populate_customers, populate_expenses, populate_shares
from models import Customers, Expenses

import pytest
from main import get_customer_by_cid, get_expenses_by_cid, get_expenses_by_cid_and_search, get_customer_by_email, get_share_by_joint_id_1, get_expense_by_id, create_expense, create_customer, delete_expense, update_customer, update_customer_budget
from models import Customers, Expenses, Shares


@pytest.fixture
def create_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    return app


@pytest.fixture
def setup_data(create_app):
    with create_app.app_context():
        db.drop_all()
        db.create_all()
        # Create a test customer
        customer1 = Customers(cid=1, email="test@test.com",
                              password="password", first_name="first", last_name="last")
        customer2 = Customers(cid=2, email="test2@test.com",
                              password="password2", first_name="first2", last_name="last2")
        db.session.add(customer1)
        db.session.add(customer2)
        db.session.commit()

        # Create some test expenses for the customer
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
        # Clean up the data after the test runs
        Expenses.query.delete()
        Customers.query.delete()
        Shares.query.delete()
        db.session.commit()


def print_database_state(create_app):
    with create_app.app_context():
        # Print all customers
        customers = db.session.query(Customers).all()
        print("Customers:")
        for customer in customers:
            print(f"ID: {customer.cid}, Email: {customer.email}, First Name: {
                  customer.first_name}, Last Name: {customer.last_name}")

        # Print all expenses
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


def test_get_customer_by_cid(create_app, setup_data):
    print_database_state(create_app)
    with create_app.app_context():
        customer = get_customer_by_cid(1)
        assert isinstance(customer, Customers)
        assert customer.cid == 1


def test_get_expenses_by_cid(create_app, setup_data):
    print_database_state(create_app)
    with create_app.app_context():
        expenses = get_expenses_by_cid(1)
        for expense in expenses:
            assert isinstance(expense[0], Expenses)
            assert expense[0].customer_id == 1


def test_get_expenses_by_cid_and_search(create_app, setup_data):
    with create_app.app_context():
        expenses = get_expenses_by_cid_and_search(1, "test")
        for expense in expenses:
            assert isinstance(expense[0], Expenses)
            assert expense[0].customer_id == 1
            assert "test" in expense[0].name


def test_get_customer_by_email(create_app, setup_data):
    with create_app.app_context():
        customer = get_customer_by_email("test@test.com")
        assert isinstance(customer, Customers)
        assert customer.email == "test@test.com"


def test_get_share_by_joint_id_1(create_app, setup_data):
    with create_app.app_context():
        share = get_share_by_joint_id_1(1)
        assert isinstance(share, Shares)
        assert share.joint_id_1 == 1


def test_get_expense_by_id(create_app, setup_data):
    with create_app.app_context():
        print_database_state(create_app)
        expense = get_expense_by_id(1)
        assert isinstance(expense, Expenses)
        assert expense.eid == 1


def test_create_expense(create_app, setup_data):
    with create_app.app_context():
        print_database_state(create_app)
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


def test_update_customer_budget(create_app, setup_data):
    with create_app.app_context():
        customer = get_customer_by_cid(1)
        update_customer_budget(customer, 200, 100)
        updated_customer = get_customer_by_cid(1)
        assert updated_customer.budget == 200
        assert updated_customer.balance == 100


@pytest.fixture
def mock_get_expenses_by_cid_and_search():
    with patch('main.get_expenses_by_cid_and_search') as mock:
        yield mock


@pytest.fixture
def mock_get_expenses_by_cid():
    with patch('main.get_expenses_by_cid') as mock:
        yield mock


@pytest.fixture
def mock_get_customer_by_email():
    with patch('main.get_customer_by_email') as mock:
        yield mock


def test_create_share(create_app, setup_data):
    with create_app.app_context():
        print_database_state(create_app)
        customer = get_customer_by_cid(1)
        joint_customer = get_customer_by_cid(2)
        create_share(customer, joint_customer)

        share = Shares.query.filter_by(joint_id_1=1).first()
        assert share is not None
        assert share.joint_id_2 == 2
        assert customer.budget == joint_customer.budget


def test_get_expense_data_without_search(mock_get_expenses_by_cid_and_search, mock_get_expenses_by_cid):
    cid = 1
    search = None
    mock_get_expenses_by_cid.return_value = [
        {'eid': 1, 'name': 'Test Expense', 'amount': 100, 'date': '2024-05-16'}]

    result = get_expense_data(cid, search)

    assert mock_get_expenses_by_cid.called
    assert not mock_get_expenses_by_cid_and_search.called
    assert result == [{'eid': 1, 'name': 'Test Expense',
                       'amount': 100, 'date': '2024-05-16'}]


def test_populate_expenses(create_app, setup_data):
    with create_app.app_context():
        # Clear the Expenses table
        Expenses.query.delete()
        db.session.commit()

        # Call the function under test
        populate_expenses()

        # Assert that the Expenses table is not empty
        expenses = Expenses.query.all()
        assert len(expenses) > 0


def test_populate_customers(create_app, setup_data):
    with create_app.app_context():
        # Clear the Customers table
        Customers.query.delete()
        db.session.commit()

        # Call the function under test
        populate_customers()

        # Assert that the Customers table is not empty
        customers = Customers.query.all()
        assert len(customers) > 0


def test_populate_shares(create_app, setup_data):
    with create_app.app_context():
        # Clear the Shares table
        Shares.query.delete()
        db.session.commit()

        # Call the function under test
        populate_shares()

        # Assert that the Shares table is not empty
        shares = Shares.query.all()
        assert len(shares) > 0
# def test_process_expense_data(create_app):
#     with create_app.app_context():
#         print_database_state(create_app)
#         data = Expenses(name="test expense", amount=100, date='2024-05-16',
#                         description="test description", customer_id=1)
#         # db.session.execute(db.select(Expenses).filter(Expenses.customer_id == cid).filter(Expenses.name.like('%'+search+'%')))
#         db.session.add(data)
#         # data = [{'eid': 1, 'name': 'Test Expense',
#         #          'amount': 100, 'date': '2024-05-16'}]
#         balance = 500

#         result = process_expense_data(data, balance)

#         assert result == [{'id': 6, 'name': 'test expense', 'amount': 100,
#                            'date': '2024-05-16', 'before': 500, 'balance': 400}]

# def test_process_expense_data(create_app, setup_data):
#     with create_app.app_context():
#         # Assuming Expenses model has an attribute 'eid' representing the expense ID
#         create_expense(
#             "test6", 100, "2022-01-01", "test description6", 1)
#         fetched_data = get_expense_by_id(6)
#         # assert fetched_data is not None  # Check if fetched data is not None

#         balance = 500
#         result = process_expense_data(fetched_data, balance)

#         assert result == [{'id': 6, 'name': "test6",
#                            'amount': 100, 'date': "2022-01-01",
#                            'before': 500, 'balance': 400}]


def test_get_budget_with_joint(create_app, setup_data):
    with create_app.app_context():
        customer1 = get_customer_by_cid(1)
        customer2 = get_customer_by_cid(2)
        customer1.joint = customer2.email
        customer2.budget = 1000
        result = get_budget(customer1)

        assert result == 1000


def test_get_budget_without_joint(create_app, setup_data):
    with create_app.app_context():
        customer1 = get_customer_by_cid(1)
        customer2 = get_customer_by_cid(2)
        customer1.budget = 500
        customer1.joint = None

        result = get_budget(customer1)

        assert result == 500


@pytest.fixture
def expense():
    expense = Expenses(name='test', amount=100,
                       date='2021-01-01', description='test', customer_id=1)
    return expense


@pytest.fixture
def user():
    user = Customers(email="test@gmail.com", password="test1234",
                     first_name="test_first", last_name="test_last")
    return user


def test_expense(expense):
    """
    GIVEN an Expense model
    WHEN a new expense is created
    THEN this expense has correct items recorded
    """

    assert expense.name == 'test'
    assert expense.amount == 100
    assert expense.date == '2021-01-01'
    assert expense.description == 'test'
    assert expense.customer_id == 1

# @pytest.fixture
# def users():
#     users = [Customers(email="user1@gmail.com",
#                        password="test", first_name="test", last_name="test"), Customers(email="user2@gmail.com",
#                                                                                         password="test", first_name="test", last_name="test")]
#     return users


# def test_register(user):
#     """
#     GIVEN a User model
#     WHEN a new User is registered
#     THEN check the email, password, first_name, last_name, balance, budget, and joint are defined correctly
#     """

#     assert user.email == "test@gmail.com"
#     assert user.password == "test1234"
#     assert user.first_name == "test_first"
#     assert user.last_name == "test_last"
#     assert user.balance == None
#     assert user.budget == None
#     assert user.joint == None


# def test_update_balance(user):
#     """
#     GIVEN a Customer model
#     WHEN balance is updated
#     THEN check the the balance before and after update
#     """
#     assert user.balance == None
#     user.balance = 1000
#     assert user.balance == 1000
#     user.joint = ""
#     assert user.balance == 1000
#     user.joint = "invalid_email"
#     assert user.balance == 1000


def test_update_budget(user):
    """
    GIVEN a Customer model
    WHEN budget is updated
    THEN check the the budget before and after update
    """
    assert user.budget == None
    user.budget = 1000
    assert user.budget == 1000
    user.joint = ""
    assert user.budget == 1000
    user.joint = "invalid_email"
    assert user.budget == 1000


if __name__ == '__main__':
    pytest.main()
