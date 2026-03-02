from app.models.base_model import BaseModel
# On importe BaseModel pour que User puisse en hériter
import hashlib
# hashlib est un module Python standard pour hacher des données (mots de passe)

class User(BaseModel):
    # User hérite de BaseModel
    # Il récupère automatiquement: id, created_at, updated_at, crud_profile
    # ainsi que les méthodes: save(), to_dict(), update()

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        # super().__init__() appelle le constructeur de BaseModel
        # Initialise id, created_at, updated_at, crud_profile

        # Validations
        if not first_name or len(first_name) > 50:
            raise ValueError("first_name is required and must be under 50 characters")

        if not last_name or len(last_name) > 50:
            raise ValueError("last_name is required and must be under 50 characters")

        if not email or "@" not in email:
            raise ValueError("A valid email is required")
            # "@" not in email vérifie qu'il y a bien un @ dans l'email

        if not password:
            raise ValueError("password is required")

        # Assignation des attributs
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = self._hash_password(password)
        # On ne stocke jamais le mot de passe en clair
        # On stocke uniquement son hash

        self.is_admin = is_admin
        # False par défaut, True uniquement pour les administrateurs

    def _hash_password(self, password):
        """Hash le mot de passe en SHA256
        
        Le _ devant le nom indique que c'est une méthode privée
        Elle ne doit pas être appelée depuis l'extérieur de la classe
        
        Exemple:
        _hash_password("secret") → "2bb80d537b1da3e38bd30361aa855686..."
        """
        return hashlib.sha256(password.encode()).hexdigest()
        # .encode() convertit la string en bytes (nécessaire pour hashlib)
        # .hexdigest() retourne le hash sous forme de string hexadécimale

    def register(self):
        """Enregistre l'utilisateur en mettant à jour son crud_profile"""
        self.crud_profile = "registered"
        self.save()
        # save() met à jour updated_at

    def update_profile(self, data):
        """Met à jour uniquement les champs autorisés du profil
        
        Exemple: user.update_profile({"first_name": "Jane"})
        """
        allowed = ['first_name', 'last_name', 'email']
        # Liste blanche des champs modifiables
        # password_hash et is_admin ne sont pas modifiables ici

        filtered = {k: v for k, v in data.items() if k in allowed}
        # Dictionnaire en compréhension : ne garde que les clés autorisées
        # ex: {"first_name": "Jane", "password": "hack"} → {"first_name": "Jane"}

        self.update(filtered)
        # Appelle BaseModel.update() avec les données filtrées

    def change_password(self, new_password):
        """Change le mot de passe de l'utilisateur"""
        if not new_password:
            raise ValueError("new password is required")
        self.password_hash = self._hash_password(new_password)
        # Hache le nouveau mot de passe avant de le stocker
        self.save()

    def delete(self):
        """Marque l'utilisateur comme supprimé"""
        self.crud_profile = "deleted"
        self.save()

    def authenticate(self, password):
        """Vérifie si le mot de passe fourni est correct
        
        Retourne True si correct, False sinon
        Exemple: user.authenticate("secret") → True
        """
        return self.password_hash == self._hash_password(password)
        # On hache le mot de passe fourni et on compare avec le hash stocké
        # On ne compare jamais en clair

    def to_dict(self):
        """Surcharge to_dict() de BaseModel pour ajouter les attributs de User
        
        IMPORTANT: password_hash n'est jamais retourné pour des raisons de sécurité
        """
        base = super().to_dict()
        # Récupère le dict de base: id, created_at, updated_at
        base.update({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
            # password_hash volontairement absent
        })
        return base
