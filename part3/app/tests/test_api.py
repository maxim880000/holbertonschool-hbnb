import unittest

from app import create_app
from app.services import facade


class UsersAPITestCase(unittest.TestCase):
    """Tests for user endpoints with admin-based access control."""

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        from app import db
        db.create_all()
        self.client = self.app.test_client()

        # Ensure we have an admin user for protected actions
        self.admin_email = 'admin@test.com'
        self.admin_password = 'adminpass'
        try:
            facade.create_user({
                'email': self.admin_email,
                'password': self.admin_password,
                'first_name': 'Admin',
                'last_name': 'User',
                'is_admin': True,
            })
        except ValueError:
            pass

        resp = self.client.post('/api/v1/users/login', json={
            'email': self.admin_email,
            'password': self.admin_password,
        })
        self.assertEqual(resp.status_code, 200)
        token = resp.get_json()['access_token']
        self.headers = {'Authorization': f'Bearer {token}'}

    def tearDown(self):
        self.ctx.pop()

    def test_user_crud_flow(self):
        # create a new user
        resp = self.client.post('/api/v1/users/', json={
            'email': 'a@b.com',
            'password': 'password',
            'first_name': 'John',
            'last_name': 'Doe'
        }, headers=self.headers)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertNotIn('password', data)
        user_id = data['id']

        # list users should include the new one
        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        arr = resp.get_json()
        self.assertIsInstance(arr, list)
        self.assertTrue(any(u['id'] == user_id for u in arr))

        # retrieve by id
        resp = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], user_id)

        # update the user
        resp = self.client.put(f'/api/v1/users/{user_id}', json={'first_name': 'Jane'}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        updated = resp.get_json()
        self.assertEqual(updated['first_name'], 'Jane')

        # 404 on missing user
        resp = self.client.get('/api/v1/users/nonexistent')
        self.assertEqual(resp.status_code, 404)

    def test_duplicate_email(self):
        payload = {
            'email': 'dup@b.com',
            'password': 'pass1234',
            'first_name': 'Alice',
            'last_name': 'Smith',
        }
        resp1 = self.client.post('/api/v1/users/', json=payload, headers=self.headers)
        self.assertEqual(resp1.status_code, 201)
        resp2 = self.client.post('/api/v1/users/', json=payload, headers=self.headers)
        self.assertEqual(resp2.status_code, 409)
        self.assertIn('message', resp2.get_json())


if __name__ == '__main__':
    unittest.main()
