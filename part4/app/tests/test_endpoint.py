"""Integration tests for all API endpoints (Users, Places, Amenities, Reviews)."""
import unittest
import uuid

from app import create_app
from app.services import facade


def _unique_email(prefix='user'):
    return f'{prefix}_{uuid.uuid4().hex[:8]}@test.com'


class BaseTestCase(unittest.TestCase):
    """Shared setUp: one fresh app + test client per test method."""

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        from app import db
        db.create_all()
        self.client = self.app.test_client()

        # Ensure we have an admin user to authenticate requests that require it
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

        self.auth_headers = self._login(self.admin_email, self.admin_password)

    def tearDown(self):
        self.ctx.pop()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _login(self, email, password):
        resp = self.client.post('/api/v1/users/login', json={
            'email': email,
            'password': password,
        })
        self.assertEqual(resp.status_code, 200)
        token = resp.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}

    def _create_user(self, email=None, first='Alice', last='Smith',
                     password='pass1234'):
        if email is None:
            email = _unique_email()
        return self.client.post('/api/v1/users/', json={
            'email': email,
            'password': password,
            'first_name': first,
            'last_name': last,
        }, headers=self.auth_headers)

    def _create_amenity(self, name='Wi-Fi'):
        return self.client.post('/api/v1/amenities/', json={'name': name}, headers=self.auth_headers)

    def _create_place(self, owner_id, amenity_ids=None, **overrides):
        payload = {
            'title': 'Test Place',
            'description': 'A test place',
            'price': 80.0,
            'latitude': 40.71,
            'longitude': -74.01,
            'owner_id': owner_id,
            'amenities': amenity_ids or [],
        }
        payload.update(overrides)
        return self.client.post('/api/v1/places/', json=payload, headers=self.auth_headers)

    def _create_review(self, user_id, place_id, rating=4, comment='Nice!'):
        return self.client.post('/api/v1/reviews/', json={
            'rating': rating,
            'comment': comment,
            'user_id': user_id,
            'place_id': place_id,
        }, headers=self.auth_headers)


# ===========================================================================
# Amenity endpoints
# ===========================================================================

class TestAmenityEndpoints(BaseTestCase):

    def test_create_amenity_success(self):
        resp = self._create_amenity('Pool')
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data['name'], 'Pool')
        self.assertIn('id', data)

    def test_create_amenity_empty_name(self):
        resp = self.client.post('/api/v1/amenities/', json={'name': ''}, headers=self.auth_headers)
        self.assertEqual(resp.status_code, 400)

    def test_create_amenity_name_too_long(self):
        resp = self.client.post('/api/v1/amenities/', json={'name': 'A' * 51}, headers=self.auth_headers)
        self.assertEqual(resp.status_code, 400)

    def test_list_amenities(self):
        self._create_amenity('Gym')
        resp = self.client.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)
        self.assertTrue(any(a['name'] == 'Gym' for a in resp.get_json()))

    def test_get_amenity_by_id(self):
        amenity_id = self._create_amenity('Parking').get_json()['id']
        resp = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], amenity_id)

    def test_get_amenity_not_found(self):
        resp = self.client.get('/api/v1/amenities/nonexistent')
        self.assertEqual(resp.status_code, 404)

    def test_update_amenity(self):
        amenity_id = self._create_amenity('Garden').get_json()['id']
        resp = self.client.put(f'/api/v1/amenities/{amenity_id}',
                               json={'name': 'Rooftop Garden'},
                               headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'Rooftop Garden')

    def test_update_amenity_not_found(self):
        resp = self.client.put('/api/v1/amenities/nonexistent',
                               json={'name': 'X'},
                               headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)


# ===========================================================================
# Place endpoints
# ===========================================================================

class TestPlaceEndpoints(BaseTestCase):

    def setUp(self):
        super().setUp()
        resp = self._create_user()
        self.owner_id = resp.get_json()['id']

    def test_create_place_success(self):
        resp = self._create_place(self.owner_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['owner_id'], self.owner_id)

    def test_non_owner_cannot_update_place(self):
        # Create a second user (non-owner) and get a token
        other_email = _unique_email('other')
        other_password = 'pass1234'
        other_user = self._create_user(email=other_email, password=other_password).get_json()
        other_headers = self._login(other_email, other_password)

        # Create a place owned by the first user
        place_id = self._create_place(self.owner_id).get_json()['id']

        resp = self.client.put(
            f'/api/v1/places/{place_id}',
            json={
                'title': 'Updated Title',
                'price': 120.0,
                'latitude': 40.71,
                'longitude': -74.01,
                'owner_id': self.owner_id,
            },
            headers=other_headers,
        )
        self.assertEqual(resp.status_code, 403)

    def test_create_place_with_amenity(self):
        amenity_id = self._create_amenity('Sauna').get_json()['id']
        resp = self._create_place(self.owner_id, amenity_ids=[amenity_id])
        self.assertEqual(resp.status_code, 201)

    def test_create_place_invalid_owner(self):
        resp = self._create_place('bad-owner-id')
        self.assertEqual(resp.status_code, 400)

    def test_create_place_empty_title(self):
        resp = self._create_place(self.owner_id, title='')
        self.assertEqual(resp.status_code, 400)

    def test_create_place_zero_price(self):
        resp = self._create_place(self.owner_id, price=0)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_negative_price(self):
        resp = self._create_place(self.owner_id, price=-5)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_latitude_out_of_range(self):
        resp = self._create_place(self.owner_id, latitude=95.0)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_longitude_out_of_range(self):
        resp = self._create_place(self.owner_id, longitude=200.0)
        self.assertEqual(resp.status_code, 400)

    def test_list_places(self):
        self._create_place(self.owner_id)
        resp = self.client.get('/api/v1/places/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)
        self.assertGreater(len(resp.get_json()), 0)

    def test_get_place_by_id(self):
        place_id = self._create_place(self.owner_id).get_json()['id']
        resp = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['id'], place_id)
        self.assertIn('owner', data)
        self.assertIn('amenities', data)

    def test_get_place_not_found(self):
        resp = self.client.get('/api/v1/places/nonexistent')
        self.assertEqual(resp.status_code, 404)

    def test_update_place(self):
        place_id = self._create_place(self.owner_id).get_json()['id']
        resp = self.client.put(f'/api/v1/places/{place_id}',
                               json={'title': 'Updated Title', 'price': 120.0,
                                     'latitude': 40.71, 'longitude': -74.01,
                                     'owner_id': self.owner_id},
                               headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)

    def test_update_place_not_found(self):
        resp = self.client.put('/api/v1/places/nonexistent',
                               json={'title': 'X', 'price': 10,
                                     'latitude': 0, 'longitude': 0,
                                     'owner_id': self.owner_id},
                               headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)


# ===========================================================================
# Review endpoints
# ===========================================================================

class TestReviewEndpoints(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user_id = self._create_user().get_json()['id']
        self.reviewer_id = self._create_user(
            email=_unique_email('reviewer'), first='Bob', last='Jones'
        ).get_json()['id']
        self.place_id = self._create_place(self.user_id).get_json()['id']

    def test_create_review_success(self):
        resp = self._create_review(self.reviewer_id, self.place_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['rating'], 4)

    def test_create_review_invalid_user(self):
        resp = self._create_review('bad-user', self.place_id)
        self.assertEqual(resp.status_code, 404)

    def test_create_review_invalid_place(self):
        resp = self._create_review(self.reviewer_id, 'bad-place')
        self.assertEqual(resp.status_code, 404)

    def test_create_review_empty_comment(self):
        resp = self._create_review(self.reviewer_id, self.place_id, comment='')
        self.assertEqual(resp.status_code, 400)

    def test_create_review_rating_too_low(self):
        resp = self._create_review(self.reviewer_id, self.place_id, rating=0)
        self.assertEqual(resp.status_code, 400)

    def test_create_review_rating_too_high(self):
        resp = self._create_review(self.reviewer_id, self.place_id, rating=6)
        self.assertEqual(resp.status_code, 400)

    def test_list_reviews(self):
        self._create_review(self.reviewer_id, self.place_id)
        resp = self.client.get('/api/v1/reviews/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_get_review_by_id(self):
        review_id = self._create_review(
            self.reviewer_id, self.place_id
        ).get_json()['id']
        resp = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], review_id)

    def test_get_review_not_found(self):
        resp = self.client.get('/api/v1/reviews/nonexistent')
        self.assertEqual(resp.status_code, 404)

    def test_update_review(self):
        review_id = self._create_review(
            self.reviewer_id, self.place_id
        ).get_json()['id']
        resp = self.client.put(f'/api/v1/reviews/{review_id}',
                               json={'rating': 5, 'comment': 'Even better!'},
                               headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['rating'], 5)

    def test_non_owner_cannot_update_review(self):
        # Create a second user and ensure they can't edit a review they don't own
        other_email = _unique_email('other')
        other_password = 'pass1234'
        other_user = self._create_user(email=other_email, password=other_password).get_json()
        other_headers = self._login(other_email, other_password)

        review_id = self._create_review(self.reviewer_id, self.place_id).get_json()['id']
        resp = self.client.put(
            f'/api/v1/reviews/{review_id}',
            json={'rating': 2, 'comment': 'Not allowed'},
            headers=other_headers,
        )
        self.assertEqual(resp.status_code, 403)

    def test_update_review_not_found(self):
        resp = self.client.put('/api/v1/reviews/nonexistent',
                               json={'rating': 3, 'comment': 'ok'},
                               headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)

    def test_delete_review(self):
        review_id = self._create_review(
            self.reviewer_id, self.place_id
        ).get_json()['id']
        resp = self.client.delete(f'/api/v1/reviews/{review_id}', headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        # Confirm it's gone
        self.assertEqual(
            self.client.get(f'/api/v1/reviews/{review_id}').status_code, 404
        )

    def test_delete_review_not_found(self):
        resp = self.client.delete('/api/v1/reviews/nonexistent', headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)

    def test_get_reviews_by_place(self):
        reviewer2_id = self._create_user(
            email=_unique_email('reviewer2'), first='Carol', last='Lee'
        ).get_json()['id']
        self._create_review(self.reviewer_id, self.place_id, comment='A')
        self._create_review(reviewer2_id, self.place_id,
                            rating=5, comment='B')
        resp = self.client.get(f'/api/v1/reviews/places/{self.place_id}/reviews')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_get_reviews_by_invalid_place(self):
        resp = self.client.get('/api/v1/reviews/places/bad-place/reviews')
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
