from app.persistence.repository import InMemoryRepository

class HBnBFacade: # section pour centraliser la logique métier de l'application, en utilisant les repositories pour gérer les données. Cette classe servira d'interface entre les ressources API et les données, en fournissant des méthodes pour créer, lire, mettre à jour et supprimer les différentes entités de l'application (utilisateurs, places, reviews, amenities).
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

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
        existing = self.user_repo.get_by_attribute('email', email)
        if existing:
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

    def get_place(self, place_id):
        pass