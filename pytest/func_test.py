from calendar import month
import pytest
from flask import url_for
from flask_testing import TestCase
from sqlalchemy import true
from main import app
from db import db
from models import Customers, Expenses
from unittest.mock import patch, MagicMock
import unittest
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
            url_for('expense_update'), data=dict(joint='test@test.com'))
        parsed_message = json.loads(response.text)
        assert parsed_message["message"] == "Set successfully! You are not sharing budget with others!"
        response = self.client.post(
            url_for('expense_update'), data=dict(joint='nick123@gmail.com'))
        parsed_message = json.loads(response.text)
        assert parsed_message["message"] == 'test!@gmail.com is successfully sharing budget with nick123@gmail.com'

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
            
            response = self.client.post(url_for('accept_month'), data=dict(months=1))
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
