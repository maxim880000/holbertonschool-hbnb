from app import db
from app.models.base_model import BaseModel

# Table d'association many-to-many entre Place et Amenity
# Doit être définie AVANT les classes qui l'utilisent
place_amenity = db.Table(
    'place_amenity',
    db.Column('place_id',   db.String(36), db.ForeignKey('places.id'),   primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True)
    # Clé primaire composite : une paire (place, amenity) est unique
)


class Place(BaseModel):
    __tablename__ = 'places'

    # Colonnes SQLAlchemy
    title        = db.Column(db.String(100),  nullable=False)
    description  = db.Column(db.String(1024), nullable=True)
    price        = db.Column(db.Float,        nullable=False)
    latitude     = db.Column(db.Float,        nullable=False)
    longitude    = db.Column(db.Float,        nullable=False)
    max_guests   = db.Column(db.Integer,      default=1)
    is_available = db.Column(db.Boolean,      default=True)

    # Clé étrangère vers User — Task 8
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    # Chaque place appartient à un seul user (many-to-one)

    # Relations SQLAlchemy — Task 8
    owner = db.relationship(
        'User',
        backref=db.backref('places', lazy=True)
        # backref crée automatiquement user.places pour accéder
        # à tous les places d'un user depuis l'objet User
    )

    amenities = db.relationship(
        'Amenity',
        secondary=place_amenity,
        lazy='subquery',
        backref=db.backref('places', lazy=True)
        # secondary pointe vers la table d'association
        # backref crée amenity.places pour l'accès inverse
    )

    reviews = db.relationship(
        'Review',
        backref=db.backref('place', lazy=True),
        lazy=True
        # backref crée review.place pour accéder au place depuis une review
    )

    def __init__(self, title, description, price, latitude,
                longitude, owner, max_guests=1, is_available=True):
        super().__init__()
        # Appelle le constructeur de BaseModel

        # Validations
        if not title or len(title) > 100:
            raise ValueError("title is required and must be under 100 characters")

        if price <= 0:
            raise ValueError("price must be a positive value (> 0)")
            # Un prix doit être strictement positif

        if not -90.0 <= latitude <= 90.0:
            raise ValueError("latitude must be between -90.0 and 90.0")
            # La latitude va de -90 (pôle sud) à +90 (pôle nord)

        if not -180.0 <= longitude <= 180.0:
            raise ValueError("longitude must be between -180.0 and 180.0")
            # La longitude va de -180 à +180

        if max_guests < 1:
            raise ValueError("max_guests must be at least 1")
            # Un lieu doit accepter au minimum 1 invité

        if owner is None:
            raise ValueError("owner is required")
            # Chaque lieu doit avoir un propriétaire (instance de User)

        # Assignation des attributs
        self.title = title
        self.description = description
        self.price = price
        # Nommé 'price' selon la consigne Holberton
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        # owner est une instance de User (relation SQLAlchemy)
        self.owner_id = owner.id
        # owner_id est la FK stockée en base

        self.max_guests = max_guests
        self.is_available = is_available
        # True par défaut : le lieu est disponible à la création

    def create(self):
        """Marque le lieu comme créé"""
        self.crud_profile = "created"
        self.save()

    def update(self, data):
        """Met à jour uniquement les champs autorisés du lieu"""
        allowed = ['title', 'description', 'price',
                'latitude', 'longitude', 'max_guests', 'is_available']
        # owner n'est pas modifiable ici
        filtered = {k: v for k, v in data.items() if k in allowed}
        super().update(filtered)

    def delete(self):
        """Marque le lieu comme supprimé"""
        self.crud_profile = "deleted"
        self.save()

    def set_availability(self, status):
        """Active ou désactive la disponibilité du lieu

        Exemple: place.set_availability(False) -> lieu non disponible
        """
        if not isinstance(status, bool):
            raise ValueError("status must be a boolean")
            # isinstance() vérifie que status est bien un booléen (True/False)
        self.is_available = status
        self.save()

    def list_amenities(self):
        """Retourne la liste des amenities du lieu"""
        return self.amenities

    def add_amenity(self, amenity):
        """Ajoute une amenity au lieu si elle n'est pas déjà présente

        Exemple: place.add_amenity(wifi_amenity)
        """
        if amenity not in self.amenities:
            # Vérifie qu'on n'ajoute pas deux fois la même amenity
            self.amenities.append(amenity)
            self.save()

    def remove_amenity(self, amenity):
        """Retire une amenity du lieu

        Exemple: place.remove_amenity(wifi_amenity)
        """
        if amenity in self.amenities:
            self.amenities.remove(amenity)
            self.save()

    def add_review(self, review):
        """Ajoute une review au lieu

        Appelée automatiquement par Review.create()
        """
        self.reviews.append(review)
        self.save()

    def get_average_rating(self):
        """Calcule et retourne la moyenne des ratings des reviews

        Retourne 0.0 si aucune review
        Exemple: [5, 4, 3] -> 4.0
        """
        if not self.reviews:
            return 0.0
            # Evite une division par zéro si pas de reviews

        return sum(r.rating for r in self.reviews) / len(self.reviews)
        # sum() additionne tous les ratings
        # len() compte le nombre de reviews
        # ex: sum([5,4,3]) / 3 = 4.0

    def to_dict(self):
        """Surcharge to_dict() pour ajouter les attributs de Place"""
        base = super().to_dict()
        base.update({
            'title': self.title,
            'description': self.description,
            'price': self.price,
            # Nommé 'price' selon la consigne Holberton
            'latitude': self.latitude,
            'longitude': self.longitude,
            'max_guests': self.max_guests,
            'is_available': self.is_available,
            'owner_id': self.owner_id,
            # On retourne l'id du owner, pas l'objet entier
            # Evite la récursion infinie dans la sérialisation JSON
            'amenities': [a.id for a in self.amenities],
            # Liste des ids des amenities (pas les objets)
            'reviews': [r.id for r in self.reviews]
            # Liste des ids des reviews (pas les objets)
        })
        return base