import unittest

from app import create_app
from app.services import facade


class AmenitiesAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        from app import db
        db.create_all()
        self.client = self.app.test_client()

        # Ensure an admin user exists for protected endpoints
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

        # Create a plain user/token for unauthorized tests
        self.user_email = 'user@test.com'
        self.user_password = 'userpass'
        try:
            facade.create_user({
                'email': self.user_email,
                'password': self.user_password,
                'first_name': 'Regular',
                'last_name': 'User',
                'is_admin': False,
            })
        except ValueError:
            pass

        resp_user = self.client.post('/api/v1/users/login', json={
            'email': self.user_email,
            'password': self.user_password,
        })
        self.assertEqual(resp_user.status_code, 200)
        user_token = resp_user.get_json()['access_token']
        self.user_headers = {'Authorization': f'Bearer {user_token}'}

    def tearDown(self):
        self.ctx.pop()

    def test_amenity_crud_flow(self):
        resp = self.client.post('/api/v1/amenities/', json={'name': 'Wi-Fi'}, headers=self.headers)
        self.assertEqual(resp.status_code, 201)
        payload = resp.get_json()
        amenity_id = payload['id']

        resp = self.client.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(item['id'] == amenity_id for item in resp.get_json()))

        resp = self.client.put(f'/api/v1/amenities/{amenity_id}', json={'name': 'Parking'}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'Parking')

        resp = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], amenity_id)

    def test_non_admin_cannot_create_amenity(self):
        resp = self.client.post('/api/v1/amenities/', json={'name': 'Sauna'}, headers=self.user_headers)
        self.assertEqual(resp.status_code, 403)

    def test_non_admin_cannot_update_amenity(self):
        # First create an amenity as admin
        amenity_id = self.client.post('/api/v1/amenities/', json={'name': 'Pool'}, headers=self.headers).get_json()['id']
        resp = self.client.put(f'/api/v1/amenities/{amenity_id}', json={'name': 'Spa'}, headers=self.user_headers)
        self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main()
