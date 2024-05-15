import pytest
from flask import url_for
from flask_testing import TestCase
from main import app
from db import db
from models import Customers, Expenses



class MyTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_index(self):
        response = self.client.get(url_for('index'))
        assert response.status_code == 302

    def test_fill(self):
        response = self.client.post(url_for('fill'))
        assert response.status_code == 200

    def test_register(self):
        response = self.client.get(url_for('register'))
        assert response.status_code == 200

    def test_reg_log_cycle(self):
        # Registration
        data = dict(email='test!@gmail.com', password='test123',
                    first_name='test', last_name='test_last')
        reg_response = self.client.post(url_for('register'), data=data)
        assert reg_response.status_code == 302

        # Login
        data = dict(email='test!@gmail.com', password='test123')
        login_response = self.client.post(url_for('login'), data=data)
        assert login_response.status_code == 302

        # Test homepage
        homepage = self.client.get(url_for('expense_homepage'))
        assert homepage.status_code == 200

        # Update
        update_response = self.client.post(url_for('expense_update'))
        assert update_response.status_code == 200

        # Expense creation and deletion
        def expense_delete(self):
            create_response = self.client.post(url_for('create'), data=dict(
                name='test', amount=100, date='2021-01-01', des='test'))
            assert create_response.status_code == 302
            id = db.session.query(Expenses).order_by(
                Expenses.eid.desc()).first()
            delete_response = self.client.post(
                url_for('expense_delete', id=id.eid))
            print(delete_response)
            assert delete_response.status_code == 302
        expense_delete(self)

        # Test update expenses
        update_expenses = self.client.get(url_for('set'))
        assert update_expenses.status_code == 200

        # Logout
        logout_response = self.client.get(url_for('logout'))
        assert logout_response.status_code == 302
        
        #Clean up
        db.session.delete(db.session.query(Customers).filter_by(email = "test!@gmail.com").first())
        db.session.commit()

    # Unit tests
    def test_expense(self):
        expense = Expenses(name='test', amount=100,
                           date='2021-01-01', description='test', customer_id=1)
        assert expense.name == 'test'
        assert expense.amount == 100
        assert expense.date == '2021-01-01'
        assert expense.description == 'test'
        assert expense.customer_id == 1

    def test_join(self):
        # Test joint function between two users
        cust_1 = Customers(email="user1@gmail.com",
                           password="test", first_name="test", last_name="test")
        cust_2 = Customers(email="user2@gmail.com",
                           password="test", first_name="test", last_name="test")
        cust_1.joint = cust_2
        assert cust_1.joint == cust_2
        assert cust_2.joint != cust_1
        assert cust_1.budget == cust_2.budget
        cust_2.joint = cust_1
        assert cust_2.joint == cust_1

    def test_register(self):
        # Test register function
        user = Customers(email="test@gmail.com", password="test1234",
                         first_name="test_first", last_name="test_last")
        assert user.email == "test@gmail.com"
        assert user.password == "test1234"
        assert user.first_name == "test_first"
        assert user.last_name == "test_last"
        assert user.balance == None
        assert user.budget == None
        assert user.joint == None
        assert user.expenses == []
        

    def test_login_true(self):
        # Test login function
        login_info = {"email": "test!@gmail.com", "password": "test123"}
        for i in db.session.query(Customers).filter_by(email=login_info["email"]):
            assert i.email == login_info["email"]
            assert i.password == login_info["password"]

    def test_login_false(self):
        # Test login function
        login_info = {"email": "new@gmail.com", "password": "test"}
        for i in db.session.query(Customers).filter_by(email=login_info["email"]):
            assert i.email != login_info["email"]
            assert i.password != login_info["password"]

    def test_delete(self):
        # Test delete function
        expense = Expenses(name='test_expense', amount=100,
                           date='2021-01-01', description='test', customer_id=1)
        db.session.add(expense)

        test_case = db.session.query(Expenses).filter_by(
            name='test_expense').first()

        assert test_case.name == 'test_expense'
        db.session.delete(expense)
        assert db.session.query(Expenses).filter_by(
            name='test_expense').first() == None


if __name__ == '__main__':
    pytest.main()
