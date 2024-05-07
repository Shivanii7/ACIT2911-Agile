import pytest
from flask import url_for
from flask_testing import TestCase
from main import app 

class MyTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_index(self):
        response = self.client.get(url_for('index'))
        assert response.status_code == 302

    def test_homepage(self):
        response = self.client.get(url_for('homepage'))
        assert response.status_code == 200

    def test_expense_homepage_get(self):
        response = self.client.get(url_for('expense_homepage_get'))
        assert response.status_code == 200

    def test_expense_homepage_post(self):
        response = self.client.post(url_for('expense_homepage'))
        assert response.status_code == 200

    def test_create(self):
        data = dict(name='test', amount=100, date='2021-01-01', des='test', cid=1)
        response = self.client.post(url_for('create'), data=data)
        assert response.status_code == 302

    def test_fill(self):
        response = self.client.post(url_for('fill'))
        assert response.status_code == 200

    def test_expense_delete(self):
        self.client.post(url_for('create'), data=dict(name='test', amount=100, date='2021-01-01', des='test', cid=1))
        id = (self.client.get(url_for('expense_homepage_get')))
        print(id)
        response = self.client.post(url_for('expense_delete', id))
        assert response.status_code == 302

    def test_register(self):
        response = self.client.get(url_for('register'))
        assert response.status_code == 200

    def test_login(self):
        response = self.client.get(url_for('login'))
        assert response.status_code == 200

    def test_logout(self):
        response = self.client.get(url_for('logout'))
        assert response.status_code == 302

    def test_set(self):
        response = self.client.get(url_for('set'))
        assert response.status_code == 200

if __name__ == '__main__':
    pytest.main()