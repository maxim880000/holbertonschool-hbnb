from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass

class BaseModel:
    def __init__(self):
        self.id = str(uuid4())
        # uuid.uuid4() génère un identifiant unique universel
        # str() le convertit en chaîne car le repo stocke des strings
        
        self.created_at = datetime.now()
        # datetime.now() capture la date et l'heure exacte de la création
        
        self.updated_at = datetime.now()
        # Même chose, sera mis à jour à chaque modification

    def save(self):
        """Appelé à chaque modification pour mettre à jour updated_at"""
        self.updated_at = datetime.now()

    def update(self, data):
        """Met à jour les attributs depuis un dictionnaire
        
        Exemple: user.update({"first_name": "Jane"})
        """
        for key, value in data.items():
            # data.items() retourne des paires (clé, valeur)
            # ex: [("first_name", "Jane"), ("email", "jane@x.com")]
            
            if hasattr(self, key):
                # hasattr vérifie que l'attribut existe sur l'objet
                # Sécurité : évite d'ajouter des attributs inconnus
                setattr(self, key, value)
                # setattr(obj, "first_name", "Jane") équivaut à obj.first_name = "Jane"
        
        self.save()  # Met à jour updated_at

    def to_dict(self):
        """Retourne un dictionnaire des attributs de base
        EX = user.to_dict() → 
        {"id": "3fa85f64...", "created_at": "2024-01-01T00:00:00", ...}
        """
        return {
            'id': self.id,
            # L'identifiant unique de l'objet
            
            'created_at': self.created_at.isoformat(),
            # .isoformat() convertit le datetime en string lisible
            # ex: datetime(2024, 1, 1) → "2024-01-01T00:00:00"
            
            'updated_at': self.updated_at.isoformat()
            # Même chose pour la date de dernière modification
        }
