"""
Full test suite for HBnB Part 3 — 50 tests covering:
  - Authentication / JWT
  - Users (CRUD + access control)
  - Places (CRUD + access control)
  - Reviews (CRUD + access control)
  - Amenities (CRUD + access control)
"""
import unittest

from app import create_app, db
from app.services import facade
from app.persistence.repository import InMemoryRepository


def _reset_facade():
    """Reset in-memory repos so tests are isolated."""
    facade.place_repo = InMemoryRepository()
    facade.review_repo = InMemoryRepository()
    facade.amenity_repo = InMemoryRepository()


class BaseTestCase(unittest.TestCase):
    """Shared setUp / tearDown for all test cases."""

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        _reset_facade()
        self.client = self.app.test_client()

        # First user created → auto-admin
        resp = self.client.post('/api/v1/users/', json={
            'email': 'admin@test.com',
            'password': 'adminpass',
            'first_name': 'Admin',
            'last_name': 'User',
        })
        self.assertEqual(resp.status_code, 201)
        self.admin_id = resp.get_json()['id']

        resp = self.client.post('/api/v1/users/login', json={
            'email': 'admin@test.com',
            'password': 'adminpass',
        })
        self.assertEqual(resp.status_code, 200)
        self.admin_token = resp.get_json()['access_token']
        self.admin_headers = {'Authorization': f'Bearer {self.admin_token}'}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        _reset_facade()
        self.ctx.pop()

    def _create_regular_user(self, email='user@test.com', password='userpass'):
        resp = self.client.post('/api/v1/users/', json={
            'email': email,
            'password': password,
            'first_name': 'Regular',
            'last_name': 'User',
        }, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 201)
        user_id = resp.get_json()['id']
        resp = self.client.post('/api/v1/users/login', json={
            'email': email,
            'password': password,
        })
        token = resp.get_json()['access_token']
        return user_id, {'Authorization': f'Bearer {token}'}

    def _create_place(self, owner_id, owner_headers, title='Test Place'):
        resp = self.client.post('/api/v1/places/', json={
            'title': title,
            'description': 'A nice place',
            'price': 50.0,
            'latitude': 48.8,
            'longitude': 2.3,
            'owner_id': owner_id,
        }, headers=owner_headers)
        self.assertEqual(resp.status_code, 201)
        return resp.get_json()['id']

    def _create_amenity(self, name='WiFi'):
        resp = self.client.post('/api/v1/amenities/', json={
            'name': name,
        }, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 201)
        return resp.get_json()['id']


# ============================================================
# 1. Authentication / JWT
# ============================================================
class TestAuthentication(BaseTestCase):

    def test_01_login_valid_credentials(self):
        """Login with correct email/password returns 200 + access_token"""
        resp = self.client.post('/api/v1/users/login', json={
            'email': 'admin@test.com',
            'password': 'adminpass',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access_token', resp.get_json())

    def test_02_login_wrong_password(self):
        """Login with wrong password returns 401"""
        resp = self.client.post('/api/v1/users/login', json={
            'email': 'admin@test.com',
            'password': 'wrongpass',
        })
        self.assertEqual(resp.status_code, 401)

    def test_03_login_missing_fields(self):
        """Login without password returns 400"""
        resp = self.client.post('/api/v1/users/login', json={
            'email': 'admin@test.com',
        })
        self.assertEqual(resp.status_code, 400)

    def test_04_me_with_valid_token(self):
        """GET /me with valid token returns 200 + user info"""
        resp = self.client.get('/api/v1/users/me', headers=self.admin_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('user', data)

    def test_05_me_without_token(self):
        """GET /me without token returns 401"""
        resp = self.client.get('/api/v1/users/me')
        self.assertEqual(resp.status_code, 401)


# ============================================================
# 2. Users
# ============================================================
class TestUsers(BaseTestCase):

    def test_06_first_user_is_admin(self):
        """First user created automatically gets is_admin=True"""
        resp = self.client.get(f'/api/v1/users/{self.admin_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()['is_admin'])

    def test_07_create_user_without_admin(self):
        """Creating a user without admin token returns 403"""
        resp = self.client.post('/api/v1/users/', json={
            'email': 'nobody@test.com',
            'password': 'pass',
            'first_name': 'No',
            'last_name': 'Body',
        })
        self.assertEqual(resp.status_code, 403)

    def test_08_create_user_duplicate_email(self):
        """Creating a user with an existing email returns 409"""
        payload = {
            'email': 'dup@test.com',
            'password': 'pass',
            'first_name': 'A',
            'last_name': 'B',
        }
        self.client.post('/api/v1/users/', json=payload, headers=self.admin_headers)
        resp = self.client.post('/api/v1/users/', json=payload, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 409)

    def test_09_list_users(self):
        """GET /users/ returns 200 and a list"""
        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_10_get_user_by_id(self):
        """GET /users/<id> returns 200 with user data"""
        resp = self.client.get(f'/api/v1/users/{self.admin_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], self.admin_id)

    def test_11_get_user_not_found(self):
        """GET /users/<bad_id> returns 404"""
        resp = self.client.get('/api/v1/users/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    def test_12_user_updates_own_name(self):
        """A user can update their own first_name / last_name"""
        user_id, headers = self._create_regular_user()
        resp = self.client.put(f'/api/v1/users/{user_id}', json={
            'first_name': 'Updated',
        }, headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['first_name'], 'Updated')

    def test_13_user_cannot_change_email(self):
        """A regular user cannot modify their own email"""
        user_id, headers = self._create_regular_user()
        resp = self.client.put(f'/api/v1/users/{user_id}', json={
            'email': 'new@test.com',
        }, headers=headers)
        self.assertEqual(resp.status_code, 400)

    def test_14_user_cannot_update_another_user(self):
        """A regular user cannot update another user's profile"""
        user_id, _ = self._create_regular_user(email='u1@test.com')
        _, headers2 = self._create_regular_user(email='u2@test.com')
        resp = self.client.put(f'/api/v1/users/{user_id}', json={
            'first_name': 'Hacker',
        }, headers=headers2)
        self.assertEqual(resp.status_code, 403)

    def test_15_admin_updates_any_user(self):
        """Admin can update any user"""
        user_id, _ = self._create_regular_user()
        resp = self.client.put(f'/api/v1/users/{user_id}', json={
            'first_name': 'AdminChanged',
        }, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['first_name'], 'AdminChanged')

    def test_16_password_not_in_response(self):
        """Password hash is never returned in user responses"""
        resp = self.client.get(f'/api/v1/users/{self.admin_id}')
        data = resp.get_json()
        self.assertNotIn('password', data)


# ============================================================
# 3. Places
# ============================================================
class TestPlaces(BaseTestCase):

    def test_17_create_place_as_owner(self):
        """Owner can create a place with their own owner_id"""
        user_id, headers = self._create_regular_user()
        resp = self.client.post('/api/v1/places/', json={
            'title': 'My Place',
            'description': 'Nice',
            'price': 100.0,
            'latitude': 10.0,
            'longitude': 20.0,
            'owner_id': user_id,
        }, headers=headers)
        self.assertEqual(resp.status_code, 201)

    def test_18_create_place_wrong_owner_id(self):
        """Non-admin cannot create a place with another user's owner_id"""
        other_id, _ = self._create_regular_user(email='other@test.com')
        _, headers = self._create_regular_user(email='me@test.com')
        resp = self.client.post('/api/v1/places/', json={
            'title': 'Stolen',
            'description': '',
            'price': 10.0,
            'latitude': 1.0,
            'longitude': 1.0,
            'owner_id': other_id,
        }, headers=headers)
        self.assertEqual(resp.status_code, 403)

    def test_19_create_place_without_token(self):
        """Creating a place without token returns 401"""
        resp = self.client.post('/api/v1/places/', json={
            'title': 'No auth',
            'description': '',
            'price': 10.0,
            'latitude': 1.0,
            'longitude': 1.0,
            'owner_id': self.admin_id,
        })
        self.assertEqual(resp.status_code, 401)

    def test_20_create_place_negative_price(self):
        """Creating a place with price <= 0 returns 400"""
        resp = self.client.post('/api/v1/places/', json={
            'title': 'Bad price',
            'description': '',
            'price': -5.0,
            'latitude': 1.0,
            'longitude': 1.0,
            'owner_id': self.admin_id,
        }, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 400)

    def test_21_create_place_invalid_latitude(self):
        """Creating a place with latitude > 90 returns 400"""
        resp = self.client.post('/api/v1/places/', json={
            'title': 'Bad lat',
            'description': '',
            'price': 10.0,
            'latitude': 200.0,
            'longitude': 1.0,
            'owner_id': self.admin_id,
        }, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 400)

    def test_22_list_places(self):
        """GET /places/ returns 200 and a list"""
        resp = self.client.get('/api/v1/places/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_23_get_place_with_owner_and_amenities(self):
        """GET /places/<id> returns owner details and amenities list"""
        place_id = self._create_place(self.admin_id, self.admin_headers)
        resp = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('owner', data)
        self.assertIn('amenities', data)

    def test_24_get_place_not_found(self):
        """GET /places/<bad_id> returns 404"""
        resp = self.client.get('/api/v1/places/nonexistent')
        self.assertEqual(resp.status_code, 404)

    def test_25_owner_updates_own_place(self):
        """Owner can update their own place"""
        user_id, headers = self._create_regular_user()
        place_id = self._create_place(user_id, headers)
        resp = self.client.put(f'/api/v1/places/{place_id}', json={
            'title': 'Updated Title',
            'description': 'New desc',
            'price': 75.0,
            'latitude': 10.0,
            'longitude': 20.0,
            'owner_id': user_id,
        }, headers=headers)
        self.assertEqual(resp.status_code, 200)

    def test_26_non_owner_cannot_update_place(self):
        """Non-owner cannot update another user's place"""
        user_id, owner_headers = self._create_regular_user(email='owner@test.com')
        _, headers2 = self._create_regular_user(email='other@test.com')
        place_id = self._create_place(user_id, owner_headers)
        resp = self.client.put(f'/api/v1/places/{place_id}', json={
            'title': 'Hacked',
            'description': '',
            'price': 1.0,
            'latitude': 1.0,
            'longitude': 1.0,
            'owner_id': user_id,
        }, headers=headers2)
        self.assertEqual(resp.status_code, 403)

    def test_27_admin_updates_any_place(self):
        """Admin can update any place"""
        user_id, headers = self._create_regular_user()
        place_id = self._create_place(user_id, headers)
        resp = self.client.put(f'/api/v1/places/{place_id}', json={
            'title': 'Admin Updated',
            'description': '',
            'price': 99.0,
            'latitude': 1.0,
            'longitude': 1.0,
            'owner_id': user_id,
        }, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 200)

    def test_28_owner_deletes_own_place(self):
        """Owner can delete their own place"""
        user_id, headers = self._create_regular_user()
        place_id = self._create_place(user_id, headers)
        resp = self.client.delete(f'/api/v1/places/{place_id}', headers=headers)
        self.assertEqual(resp.status_code, 200)

    def test_29_non_owner_cannot_delete_place(self):
        """Non-owner cannot delete another user's place"""
        user_id, owner_headers = self._create_regular_user(email='o1@test.com')
        _, headers2 = self._create_regular_user(email='o2@test.com')
        place_id = self._create_place(user_id, owner_headers)
        resp = self.client.delete(f'/api/v1/places/{place_id}', headers=headers2)
        self.assertEqual(resp.status_code, 403)


# ============================================================
# 4. Reviews
# ============================================================
class TestReviews(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Create a regular user + a place owned by admin
        self.user_id, self.user_headers = self._create_regular_user()
        self.place_id = self._create_place(self.admin_id, self.admin_headers)

    def _create_review(self, user_id, headers, place_id=None, rating=5):
        pid = place_id or self.place_id
        resp = self.client.post('/api/v1/reviews/', json={
            'rating': rating,
            'comment': 'Great place',
            'place_id': pid,
            'user_id': user_id,
        }, headers=headers)
        return resp

    def test_30_create_review_as_self(self):
        """User can create a review using their own user_id"""
        resp = self._create_review(self.user_id, self.user_headers)
        self.assertEqual(resp.status_code, 201)

    def test_31_create_review_wrong_user_id(self):
        """User cannot post a review with another user's user_id"""
        _, other_headers = self._create_regular_user(email='other@test.com')
        resp = self.client.post('/api/v1/reviews/', json={
            'rating': 4,
            'comment': 'Fake review',
            'place_id': self.place_id,
            'user_id': self.admin_id,
        }, headers=other_headers)
        self.assertEqual(resp.status_code, 403)

    def test_32_create_review_without_token(self):
        """Creating a review without token returns 401"""
        resp = self.client.post('/api/v1/reviews/', json={
            'rating': 5,
            'comment': 'No auth',
            'place_id': self.place_id,
            'user_id': self.user_id,
        })
        self.assertEqual(resp.status_code, 401)

    def test_33_create_review_invalid_rating(self):
        """Creating a review with rating 0 returns 400"""
        resp = self.client.post('/api/v1/reviews/', json={
            'rating': 0,
            'comment': 'Bad rating',
            'place_id': self.place_id,
            'user_id': self.user_id,
        }, headers=self.user_headers)
        self.assertEqual(resp.status_code, 400)

    def test_34_create_review_nonexistent_place(self):
        """Creating a review for a nonexistent place returns 404"""
        resp = self.client.post('/api/v1/reviews/', json={
            'rating': 5,
            'comment': 'Ghost place',
            'place_id': 'nonexistent-place',
            'user_id': self.user_id,
        }, headers=self.user_headers)
        self.assertEqual(resp.status_code, 404)

    def test_35_list_reviews(self):
        """GET /reviews/ returns 200 and a list"""
        resp = self.client.get('/api/v1/reviews/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_36_get_review_by_id(self):
        """GET /reviews/<id> returns 200"""
        resp = self._create_review(self.user_id, self.user_headers)
        review_id = resp.get_json()['id']
        resp = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(resp.status_code, 200)

    def test_37_get_reviews_by_place(self):
        """GET /reviews/places/<place_id>/reviews returns reviews for that place"""
        self._create_review(self.user_id, self.user_headers)
        resp = self.client.get(f'/api/v1/reviews/places/{self.place_id}/reviews')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_38_get_reviews_nonexistent_place(self):
        """GET /reviews/places/<bad_id>/reviews returns 404"""
        resp = self.client.get('/api/v1/reviews/places/nonexistent/reviews')
        self.assertEqual(resp.status_code, 404)

    def test_39_user_updates_own_review(self):
        """User can update their own review"""
        resp = self._create_review(self.user_id, self.user_headers)
        review_id = resp.get_json()['id']
        resp = self.client.put(f'/api/v1/reviews/{review_id}', json={
            'rating': 3,
            'comment': 'Changed my mind',
        }, headers=self.user_headers)
        self.assertEqual(resp.status_code, 200)

    def test_40_user_cannot_update_others_review(self):
        """User cannot update another user's review"""
        resp = self._create_review(self.user_id, self.user_headers)
        review_id = resp.get_json()['id']
        # Create a second user and try to update the first user's review
        _, headers2 = self._create_regular_user(email='intruder@test.com')
        # Create a place for intruder to be able to review (we need different place)
        place2_id = self._create_place(self.user_id, self.user_headers, title='Place2')
        # login intruder and try to modify user's review
        resp = self.client.put(f'/api/v1/reviews/{review_id}', json={
            'rating': 1,
            'comment': 'Hacked',
        }, headers=headers2)
        self.assertEqual(resp.status_code, 403)

    def test_41_user_deletes_own_review(self):
        """User can delete their own review"""
        resp = self._create_review(self.user_id, self.user_headers)
        review_id = resp.get_json()['id']
        resp = self.client.delete(f'/api/v1/reviews/{review_id}', headers=self.user_headers)
        self.assertEqual(resp.status_code, 200)

    def test_42_user_cannot_delete_others_review(self):
        """User cannot delete another user's review"""
        resp = self._create_review(self.user_id, self.user_headers)
        review_id = resp.get_json()['id']
        _, headers2 = self._create_regular_user(email='thief@test.com')
        resp = self.client.delete(f'/api/v1/reviews/{review_id}', headers=headers2)
        self.assertEqual(resp.status_code, 403)


# ============================================================
# 5. Amenities
# ============================================================
class TestAmenities(BaseTestCase):

    def test_43_admin_creates_amenity(self):
        """Admin can create an amenity"""
        resp = self.client.post('/api/v1/amenities/', json={
            'name': 'WiFi',
        }, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 201)
        self.assertIn('id', resp.get_json())

    def test_44_non_admin_cannot_create_amenity(self):
        """Regular user cannot create an amenity"""
        _, headers = self._create_regular_user()
        resp = self.client.post('/api/v1/amenities/', json={
            'name': 'Pool',
        }, headers=headers)
        self.assertEqual(resp.status_code, 403)

    def test_45_create_amenity_without_token(self):
        """Creating an amenity without token returns 401"""
        resp = self.client.post('/api/v1/amenities/', json={
            'name': 'Parking',
        })
        self.assertEqual(resp.status_code, 401)

    def test_46_list_amenities(self):
        """GET /amenities/ returns 200 and a list"""
        resp = self.client.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_47_get_amenity_by_id(self):
        """GET /amenities/<id> returns 200"""
        amenity_id = self._create_amenity('Sauna')
        resp = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'Sauna')

    def test_48_get_amenity_not_found(self):
        """GET /amenities/<bad_id> returns 404"""
        resp = self.client.get('/api/v1/amenities/nonexistent')
        self.assertEqual(resp.status_code, 404)

    def test_49_admin_updates_amenity(self):
        """Admin can update an amenity"""
        amenity_id = self._create_amenity('OldName')
        resp = self.client.put(f'/api/v1/amenities/{amenity_id}', json={
            'name': 'NewName',
        }, headers=self.admin_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'NewName')

    def test_50_non_admin_cannot_update_amenity(self):
        """Regular user cannot update an amenity"""
        amenity_id = self._create_amenity('Gym')
        _, headers = self._create_regular_user()
        resp = self.client.put(f'/api/v1/amenities/{amenity_id}', json={
            'name': 'Hacked Gym',
        }, headers=headers)
        self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main(verbosity=2)
