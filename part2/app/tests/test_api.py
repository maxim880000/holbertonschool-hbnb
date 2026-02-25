import unittest

from app import create_app


class UsersAPITestCase(unittest.TestCase):# section pour tester les endpoints de l'API liés aux utilisateurs, en vérifiant les opérations CRUD (Create, Read, Update, Delete) ainsi que les cas d'erreur comme la création d'un utilisateur avec un email déjà existant.
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_user_crud_flow(self):
        # create a new user
        resp = self.client.post('/api/v1/users/', json={
            'email': 'a@b.com',
            'password': 'password',
            'first_name': 'John',
            'last_name': 'Doe'
        })
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
        resp = self.client.put(f'/api/v1/users/{user_id}', json={'first_name': 'Jane'})
        self.assertEqual(resp.status_code, 200)
        updated = resp.get_json()
        self.assertEqual(updated['first_name'], 'Jane')

        # 404 on missing user
        resp = self.client.get('/api/v1/users/nonexistent')
        self.assertEqual(resp.status_code, 404)

    def test_duplicate_email(self):
        payload = {'email': 'dup@b.com', 'password': 'pass1234'}
        resp1 = self.client.post('/api/v1/users/', json=payload)
        self.assertEqual(resp1.status_code, 201)
        resp2 = self.client.post('/api/v1/users/', json=payload)
        self.assertEqual(resp2.status_code, 409)
        self.assertIn('message', resp2.get_json())


if __name__ == '__main__':
    unittest.main()
