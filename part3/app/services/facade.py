from __future__ import annotations

from typing import Any

from app.persistence.repository import InMemoryRepository
from app.services.repositories.user_repository import UserRepository


class HBnBFacade:
    # Centralise la logique métier de l'application, en utilisant les repositories
    # pour gérer les données. Interface entre les ressources API et les données.

    def __init__(self):
        self.user_repo    = UserRepository()
        self.place_repo   = InMemoryRepository()
        self.review_repo  = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ------------------------------------------------------------------ Users

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_users(self):
        return self.user_repo.get_all()

    def create_user(self, user_data):
        """Create a new user and persist it.

        Raises ValueError for missing fields or duplicate email.
        """
        email = user_data.get('email')
        password = user_data.get('password')
        if not email or not password:
            raise ValueError('email and password are required')
        existing = self.user_repo.get_by_attribute('email', email)
        if existing:
            raise ValueError('email already in use')
        # Allow explicit is_admin flag when provided
        from app.models.user import User
        user = User(**user_data)
        # Le hash bcrypt est appliqué dans User.__init__() via hash_password()
        # Pas besoin de le faire ici, le modèle s'en charge automatiquement
        self.user_repo.add(user)
        return user

    def update_user(self, user_id, data):
        user = self.get_user(user_id)
        if not user:
            return None
        # Si un nouveau mot de passe est fourni, on le re-hashe via bcrypt
        # On ne le passe PAS dans update() qui écrirait le hash en clair
        if 'password' in data:
            user.hash_password(data.pop('password'))

        # Validate email uniqueness if updated
        if 'email' in data:
            new_email = data['email']
            existing = self.user_repo.get_by_attribute('email', new_email)
            if existing and existing.id != user_id:
                raise ValueError('email already in use')

        user.update(data)
        return user

    # ----------------------------------------------------------------- Places

    def create_place(self, place_data):
        """Create a new place.

        Resolves owner_id → User and amenity ids → Amenity objects.
        Raises ValueError for invalid owner, amenities, or field values.
        """
        owner_id = place_data.get('owner_id')
        owner = self.get_user(owner_id)
        if not owner:
            raise ValueError('owner not found')

        amenity_ids = place_data.get('amenities') or []
        amenities = []
        for aid in amenity_ids:
            a = self.get_amenity(aid)
            if not a:
                raise ValueError(f'amenity {aid} not found')
            amenities.append(a)

        from app.models.place import Place
        place = Place(
            title=place_data['title'],
            description=place_data.get('description', ''),
            price=place_data['price'],
            latitude=place_data['latitude'],
            longitude=place_data['longitude'],
            owner=owner,
            max_guests=place_data.get('max_guests', 1),
            is_available=place_data.get('is_available', True),
        )
        for a in amenities:
            place.add_amenity(a)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, data):
        place = self.get_place(place_id)
        if not place:
            return None
        place.update(data)
        return place

    # --------------------------------------------------------------- Amenities

    def create_amenity(self, amenity_data):
        from app.models.amenity import Amenity
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, data):
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None
        amenity.update(data)
        return amenity

    # ----------------------------------------------------------------- Reviews

    def create_review(self, review_data):
        """Create a new review.

        Resolves user_id → User and place_id → Place.
        Raises ValueError when referenced entities do not exist or data is invalid.
        """
        user_id = review_data.get('user_id')
        place_id = review_data.get('place_id')
        user = self.get_user(user_id)
        if not user:
            raise ValueError('user not found')
        place = self.get_place(place_id)
        if not place:
            raise ValueError('place not found')

        if place.owner.id == user_id:
            raise ValueError('You cannot review your own place')

        existing = [r for r in self.review_repo.get_all()
                    if r.user.id == user_id and r.place.id == place_id]
        if existing:
            raise ValueError('You have already reviewed this place')

        from app.models.review import Review
        review = Review(
            rating=review_data['rating'],
            comment=review_data['comment'],
            place=place,
            user=user,
        )
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return [r for r in self.review_repo.get_all() if r.place.id == place_id]

    def update_review(self, review_id, data):
        review = self.get_review(review_id)
        if not review:
            return None
        review.update(data)
        return review

    def delete_review(self, review_id):
        self.review_repo.delete(review_id)