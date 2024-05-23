from unittest import mock
from flask import url_for
from flask_testing import TestCase
import pytest
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
        data = dict(email='test!@gmail.com', password='test123',
                    first_name='test', last_name='test_last')
        reg_response = self.client.post(url_for('register'), data=data)
        assert reg_response.status_code == 302

        # Registration fail
        data = dict(email='test!@gmail.com', password='test123',
                    first_name='test', last_name='test_last')
        reg_response = self.client.post(url_for('register'), data=data)
        assert reg_response.status_code == 302

        # Login
        data = dict(email='test!@gmail.com', password='test123')
        login_response = self.client.post(url_for('login'), data=data)
        assert login_response.status_code == 302

        # Joint
        response = self.client.post(
            url_for('expense_update'), data={'joint':'N/A','balance':0.0,'budget':0.0})
        assert b"Your status doesn't change!" in response.data

        response = self.client.post(
            url_for('expense_update'), data=dict(joint='',balance=1000.0,budget=200.0))
        assert b"Set successfully! You are not sharing budget with others!" in response.data
        
        response = self.client.post(
            url_for('expense_update'), data=dict(joint='nick123@gmail.com'))
        assert b'test!@gmail.com is successfully sharing budget with nick123@gmail.com' in response.data
        
        # Test homepage
        homepage = self.client.get(url_for('homepage'))
        assert homepage.status_code == 200

        # Create fail
        create_response = self.client.post(
            url_for('create'), data=dict(name=None))
        assert create_response.status_code == 302
        create_response = self.client.post(
            url_for('create'), data=dict(name="good", amount="abc"))
        assert create_response.status_code == 302

        # Test expense_homepage
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

            response = self.client.post(url_for('accept_month'), data=dict())
            assert response.status_code == 302

            response = self.client.post(
                url_for('accept_month'), data=dict(months=1))
            assert response.status_code == 302

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

        # Clean up
        db.session.delete(db.session.query(Customers).filter_by(
            email="test!@gmail.com").first())
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
    def test_edit_transaction(self,mock_get_transaction):
        mock_transaction=mock.Mock()
        mock_get_transaction.return_value=mock_transaction    
        data={'id':1,'name':'apple','date':'2024-02-02','amount':500.0, 'transaction_category':'expense'}
        response=self.client.post(url_for('edit_transaction'),data=data)     
        assert mock_transaction.name == 'apple'
        assert mock_transaction.date == '2024-02-02'
        assert mock_transaction.amount == '500.0'  
        assert mock_transaction.transaction_category == 'expense'
        assert response.status_code==302    
        

    @mock.patch('main.db.session.commit')
    def test_commit_failure(self,mock_commit):      
        mock_commit.side_effect = Exception('Commit failed')        
        data={'id':1,'name':'apple','date':'2024-02-02','amount':500.0}
        response=self.client.post(url_for('edit_transaction'),data=data) 
        mock_commit.assert_called_once()          
        assert response.status_code==200    
        assert b'Error: Could not save changes' in response.data


    @mock.patch('main.get_transaction_by_id')
    def test_edit_form(self,mock_get_transaction):
        mock_transaction=mock.Mock()
        mock_get_transaction.return_value=mock_transaction
        transaction_id=1
        response=self.client.get(url_for('edit_form',id=transaction_id))
        print("Response status code:", response.status_code)
        print("Response data:", response.data)
        assert response.status_code==200
        assert b'<form class="edit-form"' in response.data

        
    


