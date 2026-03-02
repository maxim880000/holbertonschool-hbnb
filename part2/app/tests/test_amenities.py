import unittest

from app import create_app


class AmenitiesAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

    def test_amenity_crud_flow(self):
        resp = self.client.post('/api/v1/amenities/', json={'name': 'Wi-Fi'})
        self.assertEqual(resp.status_code, 201)
        payload = resp.get_json()
        amenity_id = payload['id']

        resp = self.client.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(item['id'] == amenity_id for item in resp.get_json()))

        resp = self.client.put(f'/api/v1/amenities/{amenity_id}', json={'name': 'Parking'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'Parking')

        resp = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], amenity_id)


if __name__ == '__main__':
    unittest.main()
