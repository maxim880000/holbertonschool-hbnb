"""Unit tests for model validation logic."""
import unittest

from app import create_app
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

_app = create_app('testing')
_ctx = _app.app_context()
_ctx.push()
from app import db as _db
_db.create_all()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(**kwargs):
    defaults = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'password': 'secret123',
    }
    defaults.update(kwargs)
    return User(**defaults)


def make_place(owner=None, **kwargs):
    if owner is None:
        owner = make_user()
    defaults = {
        'title': 'Nice flat',
        'description': 'A cozy place',
        'price': 50.0,
        'latitude': 48.85,
        'longitude': 2.35,
        'owner': owner,
    }
    defaults.update(kwargs)
    return Place(**defaults)


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------

class TestUserModel(unittest.TestCase):

    def test_valid_user_creation(self):
        user = make_user()
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john@example.com')
        self.assertFalse(user.is_admin)
        self.assertIsNotNone(user.id)

    def test_password_is_hashed(self):
        user = make_user(password='mypassword')
        self.assertNotEqual(user.password_hash, 'mypassword')
        self.assertTrue(user.authenticate('mypassword'))
        self.assertFalse(user.authenticate('wrongpassword'))

    def test_to_dict_excludes_password(self):
        user = make_user()
        d = user.to_dict()
        self.assertNotIn('password_hash', d)
        self.assertNotIn('password', d)
        self.assertIn('id', d)
        self.assertIn('email', d)

    def test_missing_first_name(self):
        with self.assertRaises(ValueError):
            make_user(first_name='')

    def test_missing_last_name(self):
        with self.assertRaises(ValueError):
            make_user(last_name='')

    def test_missing_email(self):
        with self.assertRaises(ValueError):
            make_user(email='')

    def test_invalid_email_no_at(self):
        with self.assertRaises(ValueError):
            make_user(email='invalidemail.com')

    def test_invalid_email_no_domain(self):
        with self.assertRaises(ValueError):
            make_user(email='user@')

    def test_invalid_email_no_tld(self):
        with self.assertRaises(ValueError):
            make_user(email='user@domain')

    def test_missing_password(self):
        with self.assertRaises(ValueError):
            make_user(password='')

    def test_first_name_too_long(self):
        with self.assertRaises(ValueError):
            make_user(first_name='A' * 51)

    def test_last_name_too_long(self):
        with self.assertRaises(ValueError):
            make_user(last_name='B' * 51)

    def test_is_admin_flag(self):
        admin = make_user(is_admin=True)
        self.assertTrue(admin.is_admin)


# ---------------------------------------------------------------------------
# Place model
# ---------------------------------------------------------------------------

class TestPlaceModel(unittest.TestCase):

    def test_valid_place_creation(self):
        place = make_place()
        self.assertEqual(place.title, 'Nice flat')
        self.assertEqual(place.price, 50.0)
        self.assertEqual(place.amenities, [])
        self.assertEqual(place.reviews, [])

    def test_empty_title(self):
        with self.assertRaises(ValueError):
            make_place(title='')

    def test_title_too_long(self):
        with self.assertRaises(ValueError):
            make_place(title='T' * 101)

    def test_zero_price(self):
        with self.assertRaises(ValueError):
            make_place(price=0)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            make_place(price=-10)

    def test_latitude_too_high(self):
        with self.assertRaises(ValueError):
            make_place(latitude=91.0)

    def test_latitude_too_low(self):
        with self.assertRaises(ValueError):
            make_place(latitude=-91.0)

    def test_latitude_boundary_valid(self):
        p = make_place(latitude=90.0)
        self.assertEqual(p.latitude, 90.0)
        p2 = make_place(latitude=-90.0)
        self.assertEqual(p2.latitude, -90.0)

    def test_longitude_too_high(self):
        with self.assertRaises(ValueError):
            make_place(longitude=181.0)

    def test_longitude_too_low(self):
        with self.assertRaises(ValueError):
            make_place(longitude=-181.0)

    def test_longitude_boundary_valid(self):
        p = make_place(longitude=180.0)
        self.assertEqual(p.longitude, 180.0)
        p2 = make_place(longitude=-180.0)
        self.assertEqual(p2.longitude, -180.0)

    def test_owner_required(self):
        with self.assertRaises(ValueError):
            Place(title='X', description='', price=10.0,
                  latitude=0.0, longitude=0.0, owner=None)

    def test_add_amenity(self):
        place = make_place()
        amenity = Amenity(name='Wi-Fi')
        place.add_amenity(amenity)
        self.assertIn(amenity, place.amenities)
        # duplicate should not be added twice
        place.add_amenity(amenity)
        self.assertEqual(len(place.amenities), 1)

    def test_average_rating_no_reviews(self):
        place = make_place()
        self.assertEqual(place.get_average_rating(), 0.0)

    def test_to_dict_contains_owner_id(self):
        owner = make_user()
        place = make_place(owner=owner)
        d = place.to_dict()
        self.assertEqual(d['owner_id'], owner.id)
        self.assertNotIn('owner', d)


# ---------------------------------------------------------------------------
# Review model
# ---------------------------------------------------------------------------

class TestReviewModel(unittest.TestCase):

    def _make_review(self, **kwargs):
        owner = make_user()
        place = make_place(owner=owner)
        reviewer = make_user(email='reviewer@example.com')
        defaults = {
            'rating': 4,
            'comment': 'Great place!',
            'place': place,
            'user': reviewer,
        }
        defaults.update(kwargs)
        return Review(**defaults)

    def test_valid_review(self):
        r = self._make_review()
        self.assertEqual(r.rating, 4)
        self.assertEqual(r.comment, 'Great place!')

    def test_empty_comment(self):
        with self.assertRaises(ValueError):
            self._make_review(comment='')

    def test_rating_zero(self):
        with self.assertRaises(ValueError):
            self._make_review(rating=0)

    def test_rating_six(self):
        with self.assertRaises(ValueError):
            self._make_review(rating=6)

    def test_rating_float(self):
        with self.assertRaises(ValueError):
            self._make_review(rating=3.5)

    def test_rating_boundary_1(self):
        r = self._make_review(rating=1)
        self.assertEqual(r.rating, 1)

    def test_rating_boundary_5(self):
        r = self._make_review(rating=5)
        self.assertEqual(r.rating, 5)

    def test_missing_place(self):
        with self.assertRaises(ValueError):
            self._make_review(place=None)

    def test_missing_user(self):
        with self.assertRaises(ValueError):
            self._make_review(user=None)

    def test_to_dict_uses_ids(self):
        r = self._make_review()
        d = r.to_dict()
        self.assertIn('place_id', d)
        self.assertIn('user_id', d)
        self.assertNotIn('place', d)
        self.assertNotIn('user', d)


# ---------------------------------------------------------------------------
# Amenity model
# ---------------------------------------------------------------------------

class TestAmenityModel(unittest.TestCase):

    def test_valid_amenity(self):
        a = Amenity(name='Pool')
        self.assertEqual(a.name, 'Pool')
        self.assertEqual(a.description, '')

    def test_amenity_with_description(self):
        a = Amenity(name='Wi-Fi', description='High speed internet')
        self.assertEqual(a.description, 'High speed internet')

    def test_empty_name(self):
        with self.assertRaises(ValueError):
            Amenity(name='')

    def test_name_too_long(self):
        with self.assertRaises(ValueError):
            Amenity(name='A' * 51)

    def test_to_dict(self):
        a = Amenity(name='Parking')
        d = a.to_dict()
        self.assertEqual(d['name'], 'Parking')
        self.assertIn('id', d)


if __name__ == '__main__':
    unittest.main()
