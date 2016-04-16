from flask import Flask
from flask.ext.testing import TestCase
from app import app
import unittest


class mytest(TestCase):
    
    def create_app(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        
     #test if the login page loads correctly    
    def test_login_page_load(self):
        rv = self.app.get('/', content_type ='html/text')
        self.assertEqual(rv.status_code,'200')
        
    #test if login form behaves correctly given correct credentials
    def test_correct_login(self):
        rv = self.app.post('/', data=dict(email="sanjae_allen@hotmail.com", password="admin"),
        follow_redirects=True 
        )
        assert 'You have successfully logged in' in rv.data
    
    #test if the login page behaves correctly given incorrect credentials
    def test_incorrect_login(self):
        rv = self.app.post('/', data=dict(email="sanjae_allenhotmail.com", password="adminasdasdasdasdsadsadasdasdasdasdasdasd"),
        follow_redirects=True 
        )
        assert 'The username or password you entered is incoorect' in rv.data
    
    #test the edit user form loads with correct user id 
    def test_correct_edituser(self):
        self.app.post('/', data=dict(email="sanjae_allen@hotmail.com", password="admin"), follow_redirects=True)
        rv = self.app.post('/edituser/2')
        assertEqual(rv.status_code,'200')
    
    #test if edituser page requires someone to be logged in 
    def test_edituser_requires_login(self):
        rv = self.app.get('/edituser/1', follow_redirects=True)
        assert 'Member Login' in rv.data 
        
    
    #test if the manaageuser function requires the user to be logged in 
    def test_manageuser_requires_login(self):
        rv = self.app.get('/manageusers', follow_redirects=True)
        assert 'Member Login' in rv.data 
    
    
        
        
if __name__ == '__main__':
    unittest.main()