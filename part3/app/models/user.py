from app.models.base_model import BaseModel
import re

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class User(BaseModel):
    # User hérite de BaseModel
    # Il récupère automatiquement: id, created_at, updated_at, crud_profile
    # ainsi que les méthodes: save(), to_dict(), update()

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()

        # Validations
        if not first_name or len(first_name) > 50:
            raise ValueError("first_name is required and must be under 50 characters")

        if not last_name or len(last_name) > 50:
            raise ValueError("last_name is required and must be under 50 characters")

        if not email or not _EMAIL_RE.match(email):
            raise ValueError("A valid email is required")

        if not password:
            raise ValueError("password is required")

        # Assignation des attributs
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin

        # Le mot de passe est hashé via bcrypt, jamais stocké en clair
        self.password = ""
        self.hash_password(password)

    # ------------------------------------------------------------------ #
    #  Méthodes bcrypt (imposées par le sujet)                            #
    # ------------------------------------------------------------------ #

    def hash_password(self, password):
        """Hash le mot de passe avec bcrypt et le stocke dans self.password.

        bcrypt est supérieur à SHA256 pour les mots de passe car :
        - il intègre un salt automatique (protection contre rainbow tables)
        - il est volontairement lent (protection contre brute force)

        Exemple: hash_password("secret") → "$2b$12$..."
        """
        from app import bcrypt
        # Import ici pour éviter les imports circulaires au démarrage
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké.

        Retourne True si correct, False sinon.
        Exemple: verify_password("secret") → True
        """
        from app import bcrypt
        return bcrypt.check_password_hash(self.password, password)

    # ------------------------------------------------------------------ #
    #  Méthodes métier conservées de la Part 2                            #
    # ------------------------------------------------------------------ #

    def register(self):
        """Enregistre l'utilisateur en mettant à jour son crud_profile."""
        self.crud_profile = "registered"
        self.save()

    def update_profile(self, data):
        """Met à jour uniquement les champs autorisés du profil.

        Si 'password' est fourni, il est re-hashé via hash_password().
        Exemple: user.update_profile({"first_name": "Jane"})
        """
        allowed = ['first_name', 'last_name', 'email']
        filtered = {k: v for k, v in data.items() if k in allowed}
        self.update(filtered)

        # Le mot de passe passe par hash_password(), pas par update()
        if 'password' in data:
            self.hash_password(data['password'])

    def change_password(self, new_password):
        """Change le mot de passe de l'utilisateur (re-hash bcrypt)."""
        if not new_password:
            raise ValueError("new password is required")
        self.hash_password(new_password)
        self.save()

    def delete(self):
        """Marque l'utilisateur comme supprimé."""
        self.crud_profile = "deleted"
        self.save()

    # ------------------------------------------------------------------ #
    #  Sérialisation                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self):
        """Surcharge to_dict() de BaseModel pour ajouter les attributs User.

        IMPORTANT: self.password n'est JAMAIS retourné pour des raisons
        de sécurité. Les endpoints GET ne doivent pas exposer le hash.
        """
        base = super().to_dict()
        base.update({
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'email':      self.email,
            'is_admin':   self.is_admin,
            # 'password' volontairement absent
        })
        return base