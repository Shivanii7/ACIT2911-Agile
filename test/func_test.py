from unittest import mock
from flask import url_for
from flask_testing import TestCase
from main import app
from db import db
from models import Customers, Expenses
import json

class MyTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_homepage(self):
        response = self.client.get(url_for('homepage'))
        assert response.status_code == 302

    def test_index(self):
        response = self.client.get(url_for('index'))
        assert response.status_code == 302

    def test_fill(self):
        response = self.client.post(url_for('fill'))
        assert response.status_code == 200

    def test_login(self):
        response = self.client.get(url_for('login'))
        assert response.status_code == 200

    def test_register(self):
        response = self.client.get(url_for('register'))
        assert response.status_code == 200

    def test_reg_log_cycle(self):
        # Registration
        data = dict(email='test@gmail.com', password='test123',
                    first_name='test', last_name='test_last')
        reg_response = self.client.post(url_for('register'), data=data)
        print(reg_response.status_code)
        assert reg_response.status_code == 302

        # Attempting duplicate registration
        reg_response = self.client.post(url_for('register'), data=data)
        print(reg_response.status_code)
        assert reg_response.status_code == 302

        # Login
        data = dict(email='test@gmail.com', password='test123')
        login_response = self.client.post(url_for('login'), data=data)
        print(login_response.status_code)
        assert login_response.status_code == 302

        # Ensure user is logged in by accessing a protected route
        homepage = self.client.get(url_for('homepage'))
        print(homepage.status_code)
        assert homepage.status_code == 302

        #Joint status update
        response = self.client.post(url_for('expense_update'), data=dict(joint='N/A', balance=0.0, budget=0.0))
        print(response.data)
        assert b"Your status doesn't change!" in response.data

        response = self.client.post(url_for('expense_update'), data=dict(joint='', balance=1000.0, budget=200.0))
        print(response.data)
        assert b"Set successfully! You are not sharing budget with others!" in response.data

        response = self.client.post(url_for('expense_update'), data=dict(joint='nick123@gmail.com'))
        print(response.data)
        assert b'test@gmail.com is successfully sharing budget with nick123@gmail.com' in response.data

        # Test homepage access when logged in
        homepage = self.client.get(url_for('homepage'))
        print(homepage.status_code)
        assert homepage.status_code == 302
        
        # Test expense homepage access when logged in
        expense_homepage = self.client.get(url_for('expense_homepage'))
        print(expense_homepage.status_code)
        assert expense_homepage.status_code == 200
        
        # Test expense homepade search
        response = self.client.get(url_for('expense_homepage')+'?search='+'test')
        print(response.status_code)
        assert response.status_code == 200
        
        # Test expense homepade month
        response = self.client.get(url_for('expense_homepage')+'?month='+'01')
        print(response.status_code)
        assert response.status_code == 200

        # Log out to test protected route redirection
        self.client.get(url_for('logout'))
        homepage = self.client.get(url_for('homepage'))
        print(homepage.status_code)
        assert homepage.status_code == 302  # Expecting a redirect to login page

        # Log in again for further tests
        login_response = self.client.post(url_for('login'), data=dict(email='test@gmail.com', password='test123'))
        print(login_response.status_code)
        assert login_response.status_code == 302

        # Attempt to create an expense with invalid data
        create_response = self.client.post(url_for('create'), data=dict(name=None))
        print(create_response.status_code)
        assert create_response.status_code == 302

        create_response = self.client.post(url_for('create'), data=dict(name="good", amount="abc"))
        print(create_response.status_code)
        assert create_response.status_code == 302

        # Access the expense homepage after logging in again
        homepage = self.client.get(url_for('homepage'))
        print(homepage.status_code)
        assert homepage.status_code == 302

        # Update expenses
        update_response = self.client.post(url_for('expense_update'), data=dict(joint='', balance=500.0, budget=100.0))
        print(update_response.status_code)
        assert update_response.status_code == 200
        
        # Expense creation and deletion
        def expense_delete(self):
            create_response = self.client.post(url_for('create'), data=dict(
                name='test', amount=100, date='2021-01-01', transaction_category='expense'))
            print(create_response.status_code)
            assert create_response.status_code == 302
            id = db.session.query(Expenses).order_by(
                Expenses.eid.desc()).first()

            response = self.client.post(url_for('accept_month'), data=dict())
            print(response.status_code)
            assert response.status_code == 302

            response = self.client.post(
                url_for('accept_month'), data=dict(months=1))
            print(response.status_code)
            assert response.status_code == 302

            delete_response = self.client.post(
                url_for('expense_delete', id=id.eid))
            print(delete_response)
            print(delete_response.status_code)
            assert delete_response.status_code == 302
        expense_delete(self)

        # Test update expenses
        update_expenses = self.client.get(url_for('set'))
        print(update_expenses.status_code)
        assert update_expenses.status_code == 200

        # Logout
        logout_response = self.client.get(url_for('logout'))
        print(logout_response.status_code)
        assert logout_response.status_code == 302

        # Clean up
        db.session.delete(db.session.query(Customers).filter_by(
            email="test@gmail.com").first())
        db.session.commit()

    def test_login_fail(self):
        data = dict(email='test!?!??!@gmail.com', password='test123')
        login_response = self.client.post(url_for('login'), data=data)
        assert login_response.status_code == 302

    def test_submit_form(self):
        data = dict(search='test')
        response = self.client.post(url_for('submit_form'), data=data)
        assert response.status_code == 302

    def test_expense_homepage(self):
        response = self.client.get(url_for('expense_homepage'))
        assert response.status_code == 302

    def test_expense_update(self):
        response = self.client.post(url_for('expense_update'))
        assert response.status_code == 302

    def test_create_fail(self):
        response = self.client.post(url_for('create'))
        assert response.status_code == 302

    def test_delete_fail(self):
        response = self.client.post(url_for('expense_delete', id=0))
        assert response.status_code == 302

    def test_accept_month_fail(self):
        response = self.client.post(url_for('accept_month'))
        assert response.status_code == 302

    def test_set(self):
        response = self.client.get(url_for('set'))
        assert response.status_code == 302

    @mock.patch('main.get_transaction_by_id')
    def test_edit_transaction(self, mock_get_transaction):
        mock_transaction = mock.Mock()
        mock_get_transaction.return_value = mock_transaction
        data = {'id': 1, 'name': 'apple', 'date': '2024-02-02', 'amount': 500.0, 'transaction_category': 'expense'}
        response = self.client.post(url_for('edit_transaction'), data=data)
        assert mock_transaction.name == 'apple'
        assert mock_transaction.date == '2024-02-02'
        assert float(mock_transaction.amount) == 500.0  # Convert to float for comparison
        assert mock_transaction.transaction_category == 'expense'
        assert response.status_code == 302

    @mock.patch('main.db.session.commit')
    def test_commit_failure(self, mock_commit):
        mock_commit.side_effect = Exception('Commit failed')
        data = {'id': 1, 'name': 'apple', 'date': '2024-02-02', 'amount': 500.0}
        response = self.client.post(url_for('edit_transaction'), data=data)
        mock_commit.assert_called_once()
        assert response.status_code == 200
        assert b'Error: Could not save changes' in response.data

    @mock.patch('main.get_transaction_by_id')
    def test_edit_form(self, mock_get_transaction):
        mock_transaction = mock.Mock()
        mock_get_transaction.return_value = mock_transaction
        transaction_id = 1
        response = self.client.get(url_for('edit_form', id=transaction_id))
        print("Response status code:", response.status_code)
        print("Response data:", response.data)
        assert response.status_code == 200
        assert b'<form class="edit-form"' in response.data
