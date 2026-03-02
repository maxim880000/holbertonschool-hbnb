from app.persistence.repository import InMemoryRepository


class HBnBFacade:
    # Centralise la logique métier de l'application, en utilisant les repositories
    # pour gérer les données. Interface entre les ressources API et les données.

    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ==================================================================== #
    #  Users                                                                #
    # ==================================================================== #
    def get_user(self, user_id):
        return self.user_repo.get(user_id)

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
        if self.user_repo.get_by_attribute('email', email):
            raise ValueError('email already in use')
        from app.models.user import User
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def update_user(self, user_id, data):
        user = self.get_user(user_id)
        if not user:
            return None
        data = {k: v for k, v in data.items() if k != 'email'}
        user.update(data)
        return user

    # ==================================================================== #
    #  Amenities                                                            #
    # ==================================================================== #
    def create_amenity(self, amenity_data):
        """Create a new amenity and persist it.
        Raises ValueError if name is missing.
        """
        if not amenity_data.get('name'):
            raise ValueError('name is required')
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

    # ==================================================================== #
    #  Places                                                               #
    # ==================================================================== #
    def create_place(self, place_data):
        """Create a new place and persist it.
        Raises ValueError if owner not found or required fields are missing.
        """
        owner_id = place_data.get('owner_id')
        owner = self.user_repo.get(owner_id)
        if not owner:
            raise ValueError('owner not found')

        payload = dict(place_data)
        payload.pop('owner_id', None)

        amenities = []
        for amenity_id in payload.pop('amenity_ids', []):
            amenity = self.amenity_repo.get(amenity_id)
            if not amenity:
                raise ValueError(f'amenity {amenity_id} not found')
            amenities.append(amenity)

        from app.models.place import Place
        place = Place(owner=owner, **payload)
        for amenity in amenities:
            place.add_amenity(amenity)
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
        # owner_id is immutable after creation, same logic as email on users
        data = {k: v for k, v in data.items() if k != 'owner_id'}
        place.update(data)
        return place

    # ==================================================================== #
    #  Reviews                                                              #
    # ==================================================================== #
    def create_review(self, review_data):
        """Create a new review and persist it.
        Raises ValueError if user or place not found, or fields are missing.
        """
        user_id = review_data.get('user_id')
        place_id = review_data.get('place_id')

        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError('user not found')

        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError('place not found')

        payload = dict(review_data)
        payload.pop('user_id', None)
        payload.pop('place_id', None)

        from app.models.review import Review
        review = Review(place=place, user=user, **payload)
        place.add_review(review)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return [
            review for review in self.review_repo.get_all()
            if review.place and review.place.id == place_id
        ]

    def update_review(self, review_id, data):
        review = self.get_review(review_id)
        if not review:
            return None
        # user_id and place_id are immutable after creation
        data = {k: v for k, v in data.items() if k not in ('user_id', 'place_id')}
        review.update(data)
        return review

    def delete_review(self, review_id):
        return self.review_repo.delete(review_id)
