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
        data = dict(email='test@gmail.com', password='test', first_name='test', last_name='test')
        reg_response = self.client.post(url_for('register'), data=data)
        assert reg_response.status_code == 302

        # Login
        data = dict(email='test@gmail.com', password='test')
        login_response = self.client.post(url_for('login'), data=data)
        assert login_response.status_code == 302

        # Test homepage
        homepage = self.client.get(url_for('expense_homepage'))
        assert homepage.status_code == 200  

        # Update
        update_response = self.client.put(url_for('expense_update'))
        assert update_response.status_code == 200

        # Expense creation and deletion
        def expense_delete(self):
            create_response = self.client.post(url_for('create'), data=dict(name='test', amount=100, date='2021-01-01', des='test'))
            assert create_response.status_code == 302
            id = (self.client.get(url_for('expense_homepage')).data).decode('utf-8').count("expense_items")
            delete_response = self.client.delete(url_for('expense_delete', id=id))
            assert delete_response.status_code == 302
        expense_delete(self)

        # Test update expenses
        update_expenses = self.client.get(url_for('set'))
        assert update_expenses.status_code == 200

        # Logout
        logout_response = self.client.get(url_for('logout'))
        assert logout_response.status_code == 302

    #Unit tests
    def test_expense(self):
        expense = Expenses(name='test', amount=100, date='2021-01-01', description='test', customer_id=1)
        assert expense.name == 'test'
        assert expense.amount == 100
        assert expense.date == '2021-01-01'
        assert expense.description == 'test'
        assert expense.customer_id == 1
    
    def test_join(self):
        # Test joint function between two users
        pass
    
    def test_register(self):
        # Test register function
        new_user = {}
        
        pass
    
    def test_login(self):
        # Test login function
        pass
    
    def test_delete(self):
        # Test delete function
        pass
    
    
if __name__ == '__main__':
    pytest.main()
