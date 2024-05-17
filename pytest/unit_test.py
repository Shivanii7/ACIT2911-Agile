from unittest.mock import patch
import pytest
from sqlalchemy import StaticPool, create_engine
from main import app, create_share, get_budget, get_expense_data, process_expense_data
from db import Base, db
from manage import populate_customers, populate_expenses, populate_shares
from main import get_customer_by_cid, get_expenses_by_cid, get_expenses_by_cid_and_search, get_customer_by_email, get_share_by_joint_id_1, get_expense_by_id, create_expense, create_customer, delete_expense, update_customer, update_customer_budget
from models import Customers, Expenses, Shares
from sqlalchemy.orm import sessionmaker

'''
Build up testing database
'''


@pytest.fixture
def create_app():
    app.config['TESTING'] = True
    SQLALCHEMY_DATABASE_URL = "sqlite://"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
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
            'joint': None
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
    # print_database_state(create_app)
    with create_app.app_context():
        customer = get_customer_by_cid(1)
        assert isinstance(customer, Customers)
        assert customer.cid == 1


'''
Test get the correct expenses by cid=1
'''


def test_get_expenses_by_cid(create_app, setup_data):
    # print_database_state(create_app)
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
Test create an expense with correct name, amount, date and description
'''


def test_create_expense(create_app, setup_data):
    with create_app.app_context():
        # print_database_state(create_app)
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


@pytest.fixture
def mock_get_expenses_by_cid_and_search():
    with patch('main.get_expenses_by_cid_and_search') as mock:
        yield mock


@pytest.fixture
def mock_get_expenses_by_cid():
    with patch('main.get_expenses_by_cid') as mock:
        yield mock


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


def test_get_expense_data_with_search(mock_get_expenses_by_cid_and_search, mock_get_expenses_by_cid):
    cid = 1
    search = "Test"
    mock_get_expenses_by_cid_and_search.return_value = [
        {'eid': 1, 'name': 'Test1 Expense', 'amount': 100, 'date': '2024-05-16'}, {'eid': 2, 'name': 'Test2 Expense', 'amount': 100, 'date': '2024-05-16'}]
    result = get_expense_data(cid, search)
    assert not mock_get_expenses_by_cid.called
    assert mock_get_expenses_by_cid_and_search.called
    assert result == [
        {'eid': 1, 'name': 'Test1 Expense', 'amount': 100, 'date': '2024-05-16'}, {'eid': 2, 'name': 'Test2 Expense', 'amount': 100, 'date': '2024-05-16'}]


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
        # print_database_state(create_app)
        customer = get_customer_by_cid(1)
        joint_customer = get_customer_by_cid(2)
        create_share(customer, joint_customer)

        share = Shares.query.filter_by(joint_id_1=1).first()
        assert share is not None
        assert share.joint_id_2 == 2
        assert customer.budget == joint_customer.budget


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


if __name__ == '__main__':
    pytest.main()
