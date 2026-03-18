import re
from app import db, bcrypt
from app.models.base_model import BaseModel

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class User(BaseModel):
    __tablename__ = 'users'

    # Colonnes de la table users
    first_name = db.Column(db.String(50),  nullable=False)
    last_name  = db.Column(db.String(50),  nullable=False)
    email      = db.Column(db.String(120), nullable=False, unique=True)
    password   = db.Column(db.String(128), nullable=False)
    is_admin   = db.Column(db.Boolean,     default=False)

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError("first_name is required and must be under 50 characters")
        if not last_name or len(last_name) > 50:
            raise ValueError("last_name is required and must be under 50 characters")
        if not email or not _EMAIL_RE.match(email):
            raise ValueError("A valid email is required")
        if not password:
            raise ValueError("password is required")

        self.first_name = first_name
        self.last_name  = last_name
        self.email      = email
        self.is_admin   = is_admin
        self.password   = ""
        self.hash_password(password)

    def hash_password(self, password):
        """Hash le mot de passe avec bcrypt et le stocke dans self.password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké."""
        return bcrypt.check_password_hash(self.password, password)

    @property
    def password_hash(self):
        """Alias compatible avec les anciennes versions des tests."""
        return self.password

    def authenticate(self, password):
        """Alias compatible avec les anciennes versions des tests."""
        return self.verify_password(password)

    def update_profile(self, data):
        """Met à jour uniquement les champs autorisés du profil."""
        allowed = ['first_name', 'last_name', 'email']
        filtered = {k: v for k, v in data.items() if k in allowed}
        self.update(filtered)
        if 'password' in data:
            self.hash_password(data['password'])

    def change_password(self, new_password):
        """Change le mot de passe de l'utilisateur (re-hash bcrypt)."""
        if not new_password:
            raise ValueError("new password is required")
        self.hash_password(new_password)
        self.save()

    def to_dict(self):
        """Surcharge to_dict() — password jamais retourné."""
        base = super().to_dict()
        base.update({
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'email':      self.email,
            'is_admin':   self.is_admin,
        })
        return base
