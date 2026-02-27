from app.models.base_model import BaseModel

class Amenity(BaseModel):
    # Amenity hérite de BaseModel
    # Représente un équipement disponible dans un lieu
    # ex: "Wi-Fi", "Parking", "Piscine"

    def __init__(self, name, description=""):
        super().__init__()
        # Appelle le constructeur de BaseModel

        if not name or len(name) > 50:
            raise ValueError("name is required and must be under 50 characters")
            # not name = True si name est None ou ""

        self.name = name
        self.description = description
        # description est optionnelle, vide par défaut

    def create(self):
        """Marque l'amenity comme créée"""
        self.crud_profile = "created"
        self.save()

    def update(self, data):
        """Met à jour uniquement les champs autorisés
        
        Surcharge update() de BaseModel pour filtrer les champs
        """
        allowed = ['name', 'description']
        filtered = {k: v for k, v in data.items() if k in allowed}
        # Ne garde que name et description
        super().update(filtered)
        # Appelle BaseModel.update() avec les données filtrées

    def delete(self):
        """Marque l'amenity comme supprimée"""
        self.crud_profile = "deleted"
        self.save()

    def to_dict(self):
        """Surcharge to_dict() pour ajouter les attributs de Amenity"""
        base = super().to_dict()
        # Récupère id, created_at, updated_at
        base.update({
            'name': self.name,
            'description': self.description
        })
        return base
