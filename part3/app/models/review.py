from app import db
from app.models.base_model import BaseModel


class Review(BaseModel):
    __tablename__ = 'reviews'

    # Colonnes SQLAlchemy
    text   = db.Column(db.String(2048), nullable=False)
    rating = db.Column(db.Integer,      nullable=False)

    # Clés étrangères — Task 8
    user_id  = db.Column(db.String(36), db.ForeignKey('users.id'),  nullable=False)
    # Chaque review est écrite par un seul user
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    # Chaque review concerne un seul place

    # Relations SQLAlchemy — Task 8
    user = db.relationship(
        'User',
        backref=db.backref('reviews', lazy=True)
        # backref crée user.reviews pour accéder à toutes les
        # reviews d'un user depuis l'objet User
    )
    # Note : la relation 'place' est gérée via backref dans Place.reviews

    def __init__(self, rating, comment, place, user):
        super().__init__()
        # Appelle le constructeur de BaseModel

        # --- Validations ---
        if not comment:
            raise ValueError("comment is required")
            # not comment = True si comment est None ou ""

        if not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValueError("rating must be an integer between 1 and 5")
            # isinstance(rating, int) vérifie que c'est bien un entier
            # 1 <= rating <= 5 vérifie la plage autorisée

        if place is None:
            raise ValueError("place is required")
            # place doit être une instance de Place existante

        if user is None:
            raise ValueError("user is required")
            # user doit être une instance de User existante

        # Assignation des attributs
        self.rating = rating
        # Entier entre 1 et 5

        self.text = comment
        # Colonne SQLAlchemy nommée 'text' selon la consigne
        self.comment = comment
        # Alias gardé pour compatibilité avec le reste du code

        self.place    = place
        self.place_id = place.id
        # place est l'objet, place_id est la FK stockée en base

        self.user    = user
        self.user_id = user.id
        # user est l'objet, user_id est la FK stockée en base

    def create(self):
        """Crée la review et l'associe automatiquement au lieu"""
        self.crud_profile = "created"
        self.place.add_review(self)
        # self = l'instance Review actuelle
        # On l'ajoute directement dans la liste reviews du Place
        self.save()

    def update(self, data):
        """Met à jour uniquement les champs autorisés de la review"""
        allowed = ['rating', 'comment']
        # place et user ne sont pas modifiables après création
        filtered = {k: v for k, v in data.items() if k in allowed}

        if 'rating' in filtered:
            self.validate_rating(filtered['rating'])
            # On valide le nouveau rating avant de l'appliquer

        # renommer comment → text pour la colonne SQLAlchemy
        if 'comment' in filtered:
            filtered['text'] = filtered.pop('comment')

        super().update(filtered)
        # Appelle BaseModel.update() avec les données filtrées

    def delete(self):
        """Marque la review comme supprimée"""
        self.crud_profile = "deleted"
        self.save()

    def validate_rating(self, rating):
        """Valide que le rating est un entier entre 1 et 5
        
        Peut être appelée indépendamment pour vérifier une valeur
        Exemple: review.validate_rating(6) → ValueError
        """
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValueError("rating must be an integer between 1 and 5")

    def to_dict(self):
        """Surcharge to_dict() pour ajouter les attributs de Review"""
        base = super().to_dict()
        base.update({
            'rating': self.rating,
            'comment': self.text,
            # On retourne sous la clé 'comment' pour compatibilité API
            'place_id': self.place_id,
            # On retourne l'id du place, pas l'objet entier
            'user_id': self.user_id
            # On retourne l'id du user, pas l'objet entier
        })
        return base