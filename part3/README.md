# 🏠 HBnB — Part 2 : Application Flask REST API

> **Holberton School** — Projet HBnB (AirBnB Clone)  
> **Part 2** : Implémentation d'une API REST complète avec Flask-RESTX, architecture en couches (layered architecture), stockage en mémoire, et suite de tests automatisés.

---

## 📋 Table des matières

1. [Vue d'ensemble du projet](#-vue-densemble-du-projet)
2. [Architecture globale](#-architecture-globale)
3. [Tableau complet des fichiers](#-tableau-complet-des-fichiers)
4. [Arborescence annotée](#-arborescence-annotée)
5. [Explication détaillée de chaque fichier](#-explication-détaillée-de-chaque-fichier)
   - [run.py](#-runpy--point-dentrée-de-lapplication)
   - [config.py (racine)](#-configpy-racine--configuration-multi-environnement)
   - [requirements.txt](#-requirementstxt--dépendances-python)
   - [app/\_\_init\_\_.py](#-app__init__py--factory-flask)
   - [app/config.py](#-appconfigpy--configuration-applicative)
   - [app/models/base\_model.py](#-appmodelsbase_modelpy--classe-de-base)
   - [app/models/user.py](#-appmodelsuserpy--modèle-utilisateur)
   - [app/models/place.py](#-appmodelsplacepy--modèle-lieu)
   - [app/models/amenity.py](#-appmodelsamenitypy--modèle-équipement)
   - [app/models/review.py](#-appmodelsreviewpy--modèle-avis)
   - [app/models/entities.py](#-appmodelsentitiespy--entités-dataclass)
   - [app/persistence/repository.py](#-apppersistencerepositorypy--couche-de-persistance)
   - [app/services/facade.py](#-appservicesfacadepy--façade-métier)
   - [app/services/\_\_init\_\_.py](#-appservices__init__py--singleton-de-la-façade)
   - [app/api/\_\_init\_\_.py](#-appapi__init__py--blueprint-api)
   - [app/api/amenities.py](#-appapiamenitiespy--namespace-amenities-alternatif)
   - [app/api/v1/users.py](#-appapiv1userspy--endpoints-utilisateurs)
   - [app/api/v1/amenities.py](#-appapiv1amenitiespy--endpoints-équipements)
   - [app/api/v1/places.py](#-appapiv1placespy--endpoints-lieux)
   - [app/api/v1/reviews.py](#-appapiv1reviewspy--endpoints-avis)
   - [app/tests/test\_models.py](#-appteststest_modelspy--tests-unitaires-modèles)
   - [app/tests/test\_api.py](#-appteststest_apipy--tests-api-utilisateurs)
   - [app/tests/test\_amenities.py](#-appteststest_amenitiespy--tests-api-amenities)
   - [app/tests/test\_endpoint.py](#-appteststest_endpointpy--tests-dintégration-complets)
   - [app/tests/tests\_report.md](#-apptekststests_reportmd--rapport-de-tests)
   - [curl\_tests.sh](#-curl_testssh--tests-manuels-curl)
6. [Patterns architecturaux](#-patterns-architecturaux)
7. [Modèles de données & validations](#-modèles-de-données--validations)
8. [Endpoints de l'API](#-endpoints-de-lapi)
9. [Flux de données](#-flux-de-données)
10. [Lancer le projet](#-lancer-le-projet)
11. [Lancer les tests](#-lancer-les-tests)

---

## 🌍 Vue d'ensemble du projet

HBnB Part 2 est une **API REST** qui simule le backend d'une plateforme de location de logements (style AirBnB). Elle expose 4 ressources principales accessibles via HTTP :

| Ressource   | Description                                       | Endpoint de base        |
|-------------|---------------------------------------------------|-------------------------|
| **Users**   | Utilisateurs (propriétaires et locataires)        | `/api/v1/users/`        |
| **Places**  | Logements disponibles à la location               | `/api/v1/places/`       |
| **Amenities** | Équipements disponibles dans les logements      | `/api/v1/amenities/`    |
| **Reviews** | Avis laissés par des utilisateurs sur des lieux   | `/api/v1/reviews/`      |

**Technologies utilisées :**
- 🐍 Python 3
- 🌶️ Flask (framework web)
- 📚 Flask-RESTX (extensions REST + Swagger auto)
- 🧪 `unittest` (tests unitaires et intégration)
- 🗃️ Stockage en mémoire (dict Python, pas de base de données)

---

## 🏛️ Architecture globale

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (curl / HTTP)                 │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP Request
┌──────────────────────────▼──────────────────────────────┐
│              COUCHE API  (app/api/v1/*.py)              │
│   Flask-RESTX Namespaces • Validation entrée/sortie     │
│   Swagger UI auto-généré à /doc                         │
└──────────────────────────┬──────────────────────────────┘
                           │ appelle
┌──────────────────────────▼──────────────────────────────┐
│           COUCHE SERVICE  (app/services/facade.py)      │
│   HBnBFacade • Logique métier • Résolution des IDs      │
│   Interface unique entre API et données                 │
└──────────────────────────┬──────────────────────────────┘
                           │ appelle
┌──────────────────────────▼────────────────────────────────┐
│        COUCHE PERSISTANCE  (app/persistence/repository.py)│
│   InMemoryRepository • CRUD générique                     │
│   Stockage dict Python (en mémoire, reset au redémarrage) │
└──────────────────────────┬────────────────────────────────┘
                           │ retourne des objets
┌──────────────────────────▼──────────────────────────────┐
│           COUCHE MODÈLES  (app/models/*.py)             │
│   User • Place • Amenity • Review • BaseModel           │
│   Validation des données • Sérialisation JSON           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Tableau complet des fichiers

| # | Chemin complet | Type | Rôle principal |
|---|----------------|------|----------------|
| 1 | `run.py` | Point d'entrée | Lance le serveur Flask en mode développement |
| 2 | `config.py` | Configuration | Classes de config Development/Testing/Production (racine) |
| 3 | `requirements.txt` | Dépendances | Liste des packages Python nécessaires |
| 4 | `curl_tests.sh` | Script bash | Tests manuels de tous les endpoints via cURL |
| 5 | `__init__.py` | Init Python | Package racine |
| 6 | `app/__init__.py` | **Factory Flask** | Crée l'application Flask, configure l'API, enregistre les namespaces |
| 7 | `app/config.py` | Configuration | Classes de config utilisées par la factory (dupliqué intentionnel) |
| 8 | `app/api/__init__.py` | Blueprint | Déclare le Blueprint API v1 et importe les namespaces |
| 9 | `app/api/amenities.py` | Namespace alt. | Version alternative du namespace Amenities (pédagogique) |
| 10 | `app/api/v1/__init__.py` | Init Python | Package API v1 |
| 11 | `app/api/v1/users.py` | **Endpoints** | CRUD complet des utilisateurs : GET/POST/PUT |
| 12 | `app/api/v1/places.py` | **Endpoints** | CRUD complet des lieux : GET/POST/PUT |
| 13 | `app/api/v1/amenities.py` | **Endpoints** | CRUD complet des équipements : GET/POST/PUT |
| 14 | `app/api/v1/reviews.py` | **Endpoints** | CRUD complet des avis : GET/POST/PUT/DELETE |
| 15 | `app/models/__init__.py` | Init Python | Package modèles |
| 16 | `app/models/base_model.py` | **Modèle base** | Classe parente : `id`, `created_at`, `updated_at`, `save()`, `to_dict()` |
| 17 | `app/models/user.py` | **Modèle** | Utilisateur : validation email/nom, hachage mot de passe SHA256 |
| 18 | `app/models/place.py` | **Modèle** | Lieu : validation géo/prix, gestion amenities et reviews |
| 19 | `app/models/amenity.py` | **Modèle** | Équipement : validation nom max 50 chars |
| 20 | `app/models/review.py` | **Modèle** | Avis : validation rating 1-5, comment obligatoire |
| 21 | `app/models/entities.py` | Entités dataclass | Version `@dataclass` des 4 entités (User/Place/Amenity/Review) |
| 22 | `app/persistence/repository.py` | **Persistance** | Interface `Repository` (ABC) + `InMemoryRepository` (dict) |
| 23 | `app/services/__init__.py` | **Service** | Instancie un singleton global `HBnBFacade` |
| 24 | `app/services/facade.py` | **Façade** | `HBnBFacade` : toute la logique métier CRUD pour les 4 ressources |
| 25 | `app/tests/test_models.py` | **Tests unitaires** | 43 tests de validation des modèles (sans Flask) |
| 26 | `app/tests/test_api.py` | **Tests API** | Tests CRUD et email dupliqué pour Users |
| 27 | `app/tests/test_amenities.py` | **Tests API** | Tests CRUD complets pour Amenities |
| 28 | `app/tests/test_endpoint.py` | **Tests intégration** | 36 tests couvrant tous les endpoints (Users/Places/Amenities/Reviews) |
| 29 | `app/tests/tests_report.md` | Rapport | Rapport complet : 81/81 tests passés, tableaux de validation |

---

## 🗂️ Arborescence annotée

```
part2/
│
├── run.py                    ← DÉMARRER LE SERVEUR ICI
├── config.py                 ← Config multi-env (dev/test/prod) — racine
├── requirements.txt          ← flask + flask-restx
├── curl_tests.sh             ← Tous les tests cURL en 1 script
├── __init__.py
│
└── app/                      ← Package principal de l'application
    ├── __init__.py           ← create_app() : factory pattern Flask
    ├── config.py             ← Même config que la racine (utilisée par la factory)
    │
    ├── api/                  ← Couche présentation (HTTP)
    │   ├── __init__.py       ← Blueprint API v1
    │   ├── amenities.py      ← Namespace amenities alternatif
    │   └── v1/               ← Version 1 de l'API
    │       ├── __init__.py
    │       ├── users.py      ← GET/POST /users/, GET/PUT /users/<id>
    │       ├── places.py     ← GET/POST /places/, GET/PUT /places/<id>
    │       ├── amenities.py  ← GET/POST /amenities/, GET/PUT /amenities/<id>
    │       └── reviews.py    ← GET/POST /reviews/, GET/PUT/DELETE /reviews/<id>
    │
    ├── models/               ← Couche métier : entités et validations
    │   ├── __init__.py
    │   ├── base_model.py     ← BaseModel : id UUID, timestamps, save(), to_dict()
    │   ├── user.py           ← User(BaseModel) : email regex, password SHA256
    │   ├── place.py          ← Place(BaseModel) : geo validation, amenities list
    │   ├── amenity.py        ← Amenity(BaseModel) : name max 50 chars
    │   ├── review.py         ← Review(BaseModel) : rating 1-5, comment non vide
    │   └── entities.py       ← @dataclass versions des 4 entités
    │
    ├── persistence/          ← Couche données
    │   └── repository.py     ← ABC Repository + InMemoryRepository (dict)
    │
    ├── services/             ← Couche service (logique métier centralisée)
    │   ├── __init__.py       ← facade = HBnBFacade() singleton
    │   └── facade.py         ← HBnBFacade : CRUD pour User/Place/Amenity/Review
    │
    └── tests/                ← Suite de tests
        ├── test_models.py    ← 43 tests unitaires modèles
        ├── test_api.py       ← Tests CRUD Users
        ├── test_amenities.py ← Tests CRUD Amenities
        ├── test_endpoint.py  ← 36 tests intégration tous endpoints
        └── tests_report.md   ← Rapport 81/81 PASS
```

---

## 📖 Explication détaillée de chaque fichier

---

### 🚀 `run.py` — Point d'entrée de l'application

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

**Rôle :** C'est le fichier qu'on exécute pour démarrer le serveur.

| Ligne | Explication |
|-------|-------------|
| `from app import create_app` | Importe la fonction factory depuis `app/__init__.py` |
| `app = create_app()` | Crée l'application Flask avec la config par défaut (`development`) |
| `if __name__ == '__main__':` | Condition Python standard : ce bloc ne s'exécute que si on lance directement `python run.py`, pas si le fichier est importé |
| `app.run(debug=True)` | Lance le serveur de développement Flask sur `http://127.0.0.1:5000`. `debug=True` active le rechargement automatique et les messages d'erreur détaillés |

**Comment l'utiliser :**
```bash
python run.py
# → Serveur disponible sur http://127.0.0.1:5000
# → Documentation Swagger sur http://127.0.0.1:5000/doc
```

---

### ⚙️ `config.py` (racine) — Configuration multi-environnement

```python
import os

class Config:
    """Configuration de base partagée par tous les environnements."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Configuration pour le développement local."""
    DEBUG = True

class TestingConfig(Config):
    """Configuration pour la suite de tests."""
    TESTING = True
    DEBUG = False

class ProductionConfig(Config):
    """Configuration pour la production."""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing':     TestingConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
```

**Rôle :** Définit les paramètres de configuration selon l'environnement.

| Classe | `DEBUG` | `TESTING` | Usage |
|--------|---------|-----------|-------|
| `Config` | `False` | `False` | Base commune |
| `DevelopmentConfig` | `True` | `False` | Dev local, rechargement auto |
| `TestingConfig` | `False` | `True` | Suite de tests, pas de gestion d'erreurs Flask |
| `ProductionConfig` | `False` | `False` | Déploiement en production |

**Points clés :**
- `SECRET_KEY` : utilisée pour signer les sessions Flask. En production, **doit** être définie via variable d'environnement `os.getenv('SECRET_KEY', ...)`.
- `TESTING = True` : désactive la gestion interne des exceptions Flask → les erreurs remontent directement dans les tests.
- Le dictionnaire `config` permet de sélectionner la config par un nom de string (ex: `config['development']`).

---

### 📦 `requirements.txt` — Dépendances Python

```
flask
flask-restx
```

**Rôle :** Déclare les packages Python nécessaires au projet.

| Package | Version | Rôle |
|---------|---------|------|
| `flask` | dernière stable | Framework web léger pour Python. Gère le routing HTTP, les requêtes/réponses, le contexte d'application |
| `flask-restx` | dernière stable | Extension Flask pour construire des APIs REST. Ajoute : Namespaces, validation automatique, génération de documentation Swagger UI |

**Installation :**
```bash
pip install -r requirements.txt
```

---

### 🏭 `app/__init__.py` — Factory Flask

```python
from flask import Flask
from flask_restx import Api
from app.config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/doc',
    )

    from app.api.v1.users import api as users_ns
    api.add_namespace(users_ns, path='/api/v1/users')

    from app.api.v1.places import api as places_ns
    api.add_namespace(places_ns, path='/api/v1/places')

    from app.api.v1.amenities import api as amenities_ns
    api.add_namespace(amenities_ns, path='/api/v1/amenities')

    from app.api.v1.reviews import api as reviews_ns
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
```

**Rôle :** C'est le cœur de l'application. Utilise le **Factory Pattern** pour créer et configurer Flask.

| Étape | Code | Explication |
|-------|------|-------------|
| 1 | `app = Flask(__name__)` | Crée l'instance Flask. `__name__` = `'app'`, indique à Flask où chercher les templates/static |
| 2 | `app.config.from_object(config[config_name])` | Charge la configuration selon l'environnement. Ex: `config['development']` → `DevelopmentConfig` |
| 3 | `api = Api(app, ...)` | Crée l'API Flask-RESTX. `doc='/doc'` → Swagger UI accessible à `http://localhost:5000/doc` |
| 4 | `from app.api.v1.users import ...` | Import **à l'intérieur de la fonction** pour éviter les imports circulaires |
| 5 | `api.add_namespace(users_ns, path='/api/v1/users')` | Enregistre le namespace Users : toutes ses routes seront préfixées par `/api/v1/users` |
| 6 | `return app` | Retourne l'application configurée |

**Pourquoi le Factory Pattern ?**
- Permet de créer plusieurs instances avec des configs différentes (dev, test, prod)
- Évite les problèmes d'état global
- Facilite les tests : `create_app('testing')` crée une app de test isolée

---

### ⚙️ `app/config.py` — Configuration applicative

```python
import os

class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

class TestingConfig:
    DEBUG = False
    TESTING = True
    SECRET_KEY = "test-secret-key"

class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
```

**Rôle :** Même logique que `config.py` à la racine, mais c'est **ce fichier** qui est importé par la factory `app/__init__.py`. Version légèrement simplifiée (pas de classe `Config` parente).

> ⚠️ **Note :** Il existe deux fichiers `config.py` dans le projet (racine et `app/`). C'est `app/config.py` qui est réellement utilisé par l'application via `from app.config import config`.

---

### 🧬 `app/models/base_model.py` — Classe de base

> Ce fichier contient **deux implémentations** — une version dataclass et une version classique. La version classique est celle utilisée par les modèles.

**Version classique (utilisée en pratique) :**

```python
import uuid
from datetime import datetime

class BaseModel:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        self.updated_at = datetime.now()

    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
```

**Rôle :** Classe parente de tous les modèles. Fournit les comportements communs.

| Attribut/Méthode | Type | Explication détaillée |
|-----------------|------|-----------------------|
| `id` | `str` | Identifiant unique universel généré par `uuid.uuid4()`. Format : `"3fa85f64-5717-4562-b3fc-2c963f66afa6"`. Converti en `str` car le repository stocke des strings comme clés de dict |
| `created_at` | `datetime` | Timestamp de création. Capturé avec `datetime.now()` au moment de l'instanciation |
| `updated_at` | `datetime` | Timestamp de dernière modification. Mis à jour automatiquement par `save()` |
| `save()` | méthode | Met `updated_at` à l'heure actuelle. Appelée après chaque modification |
| `update(data)` | méthode | Prend un dict `{"clé": valeur}`, met à jour les attributs existants (protection via `hasattr`), puis appelle `save()` |
| `to_dict()` | méthode | Sérialise l'objet en dict Python. Les `datetime` sont convertis en ISO 8601 (string) pour être sérialisables en JSON |

**Héritage :**
```
BaseModel
    ├── User
    ├── Place
    ├── Amenity
    └── Review
```

---

### 👤 `app/models/user.py` — Modèle utilisateur

```python
from app.models.base_model import BaseModel
import hashlib
import re

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

class User(BaseModel):
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

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = self._hash_password(password)
        self.is_admin = is_admin

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, password):
        return self.password_hash == self._hash_password(password)

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
            # password_hash volontairement absent
        })
        return base
```

**Rôle :** Représente un utilisateur de la plateforme.

| Attribut | Type | Contrainte | Explication |
|----------|------|-----------|-------------|
| `first_name` | `str` | Requis, max 50 chars | Prénom de l'utilisateur |
| `last_name` | `str` | Requis, max 50 chars | Nom de famille |
| `email` | `str` | Requis, format valide | Adresse email, vérifiée par regex |
| `password_hash` | `str` | Jamais exposé | Hash SHA256 du mot de passe. **Jamais le mot de passe en clair** |
| `is_admin` | `bool` | `False` par défaut | Drapeau d'administrateur |

**Sécurité du mot de passe :**

```
password "secret"
    ↓ .encode() → bytes b"secret"
    ↓ hashlib.sha256() → objet SHA256
    ↓ .hexdigest() → "2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b"
```

- `hashlib.sha256` : algorithme de hachage cryptographique standard
- `.encode()` : convertit la string en bytes (requis par hashlib)
- `.hexdigest()` : retourne le hash en hexadécimal (64 chars)
- **`to_dict()` n'inclut jamais `password_hash`** → protection automatique contre l'exposition

**Validation de l'email :**

```
Regex : ^[^@\s]+@[^@\s]+\.[^@\s]+$
         ↑        ↑        ↑
     partie    domaine    TLD
     locale    (@domain)  (.com)
```

| Email | Valide ? |
|-------|----------|
| `alice@example.com` | ✅ |
| `alice@example` | ❌ (pas de TLD) |
| `invalidemail.com` | ❌ (pas de @) |
| `alice@` | ❌ (pas de domaine) |

---

### 🏡 `app/models/place.py` — Modèle lieu

```python
from app.models.base_model import BaseModel

class Place(BaseModel):
    def __init__(self, title, description, price, latitude,
                longitude, owner, max_guests=1, is_available=True):
        super().__init__()
        # Validations
        if not title or len(title) > 100:
            raise ValueError("title is required and must be under 100 characters")
        if price <= 0:
            raise ValueError("price must be a positive value (> 0)")
        if not -90.0 <= latitude <= 90.0:
            raise ValueError("latitude must be between -90.0 and 90.0")
        if not -180.0 <= longitude <= 180.0:
            raise ValueError("longitude must be between -180.0 and 180.0")
        if max_guests < 1:
            raise ValueError("max_guests must be at least 1")
        if owner is None:
            raise ValueError("owner is required")

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner       # Instance de User
        self.max_guests = max_guests
        self.is_available = is_available
        self.reviews = []        # Liste de Review
        self.amenities = []      # Liste de Amenity
```

**Rôle :** Représente un logement disponible à la location.

| Attribut | Type | Contrainte | Explication |
|----------|------|-----------|-------------|
| `title` | `str` | Requis, max 100 chars | Titre du logement |
| `description` | `str` | Optionnel | Description détaillée |
| `price` | `float` | Strictement positif (> 0) | Prix par nuit en € |
| `latitude` | `float` | `[-90.0, 90.0]` | Latitude GPS. -90 = Pôle Sud, +90 = Pôle Nord |
| `longitude` | `float` | `[-180.0, 180.0]` | Longitude GPS. -180/+180 = ligne internationale |
| `owner` | `User` | Requis | Instance de User (propriétaire) |
| `max_guests` | `int` | >= 1, défaut 1 | Capacité maximale |
| `is_available` | `bool` | `True` par défaut | Disponibilité |
| `reviews` | `list[Review]` | Initialisée vide | Relation 1-N avec Review |
| `amenities` | `list[Amenity]` | Initialisée vide | Relation N-N avec Amenity |

**Méthodes importantes :**

| Méthode | Retour | Explication |
|---------|--------|-------------|
| `add_amenity(amenity)` | `None` | Ajoute si pas déjà présent (pas de doublons) |
| `remove_amenity(amenity)` | `None` | Retire si présent |
| `add_review(review)` | `None` | Ajoute un avis à la liste |
| `get_average_rating()` | `float` | Moyenne des ratings. `0.0` si aucun avis (évite division par zéro) |
| `set_availability(status)` | `None` | Active/désactive le lieu. Valide que `status` est un `bool` |
| `update(data)` | `None` | Surcharge : seuls `title, description, price, latitude, longitude, max_guests, is_available` sont modifiables |

**Sérialisation (`to_dict`) :**

```python
{
    'id': '...',
    'title': 'Belle villa',
    'owner_id': 'abc123',     # ID seulement, pas l'objet User complet
    'amenities': ['id1', 'id2']  # IDs seulement
}
```

> ⚠️ On ne sérialise **jamais** les objets imbriqués complets (évite la récursion infinie). On retourne uniquement les IDs.

---

### 🏊 `app/models/amenity.py` — Modèle équipement

```python
from app.models.base_model import BaseModel

class Amenity(BaseModel):
    def __init__(self, name, description=""):
        super().__init__()
        if not name or len(name) > 50:
            raise ValueError("name is required and must be under 50 characters")
        self.name = name
        self.description = description

    def update(self, data):
        allowed = ['name', 'description']
        filtered = {k: v for k, v in data.items() if k in allowed}
        super().update(filtered)

    def to_dict(self):
        base = super().to_dict()
        base.update({'name': self.name, 'description': self.description})
        return base
```

**Rôle :** Représente un équipement/service disponible dans un logement (Wi-Fi, Parking, Piscine...).

| Attribut | Type | Contrainte | Exemple |
|----------|------|-----------|---------|
| `name` | `str` | Requis, max 50 chars | `"Wi-Fi"`, `"Parking"`, `"Piscine"` |
| `description` | `str` | Optionnel, vide par défaut | `"Connexion haut débit"` |

**Pattern liste blanche dans `update()` :**
```python
allowed = ['name', 'description']
filtered = {k: v for k, v in data.items() if k in allowed}
```
Cette technique filtre les données entrantes : seuls les champs autorisés sont modifiés. Si un client envoie `{"id": "hack", "name": "Nouveau nom"}`, seul `name` sera mis à jour.

---

### ⭐ `app/models/review.py` — Modèle avis

```python
from app.models.base_model import BaseModel

class Review(BaseModel):
    def __init__(self, rating, comment, place, user):
        super().__init__()
        if not comment:
            raise ValueError("comment is required")
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValueError("rating must be an integer between 1 and 5")
        if place is None:
            raise ValueError("place is required")
        if user is None:
            raise ValueError("user is required")

        self.rating = rating
        self.comment = comment
        self.place = place   # Instance de Place
        self.user = user     # Instance de User

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'rating': self.rating,
            'comment': self.comment,
            'place_id': self.place.id,   # ID seulement
            'user_id': self.user.id      # ID seulement
        })
        return base
```

**Rôle :** Représente un avis laissé par un utilisateur sur un logement.

| Attribut | Type | Contrainte | Explication |
|----------|------|-----------|-------------|
| `rating` | `int` | Entier entre 1 et 5 | Note. `isinstance(rating, int)` rejette les floats (3.5 invalide) |
| `comment` | `str` | Requis, non vide | Texte de l'avis |
| `place` | `Place` | Requis | Instance de Place (relation) |
| `user` | `User` | Requis | Instance de User (auteur de l'avis) |

**Validation du rating :**
```python
not isinstance(rating, int) or not 1 <= rating <= 5
```
- `isinstance(rating, int)` : vérifie que c'est un entier (pas un float)
- `1 <= rating <= 5` : syntaxe Python d'enchaînement de comparaisons (équivalent à `rating >= 1 and rating <= 5`)

---

### 🗂️ `app/models/entities.py` — Entités dataclass

```python
from __future__ import annotations
from dataclasses import dataclass, field
from app.models.base_model import BaseModel

@dataclass
class User(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: str = ""

    def __post_init__(self) -> None:
        if not self.first_name or not self.last_name:
            raise ValueError("first_name and last_name are required")
        if "@" not in self.email:
            raise ValueError("email must be valid")

@dataclass
class Amenity(BaseModel):
    name: str = ""
    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")

@dataclass
class Place(BaseModel):
    title: str = ""
    description: str = ""
    price: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    owner_id: str = ""
    amenity_ids: list[str] = field(default_factory=list)
    review_ids: list[str] = field(default_factory=list)
    # ... validations dans __post_init__

@dataclass
class Review(BaseModel):
    text: str = ""
    user_id: str = ""
    place_id: str = ""
    # ... validations dans __post_init__
```

**Rôle :** Version alternative des 4 entités utilisant le décorateur `@dataclass` de Python. Utilisée par la `HBnBFacade`.

**Différences avec les modèles classiques :**

| Aspect | `models/user.py` | `models/entities.py` |
|--------|-----------------|----------------------|
| Style | Classe Python classique | `@dataclass` |
| Validation | Dans `__init__` | Dans `__post_init__` |
| Relations | Objets imbriqués (ex: `owner=User(...)`) | IDs uniquement (ex: `owner_id="abc"`) |
| Usage | Instanciation directe | Via la Façade |

**Pourquoi `@dataclass` ?**
- Génère automatiquement `__init__`, `__repr__`, `__eq__`
- Moins de code boilerplate
- `field(default_factory=list)` : crée une nouvelle liste pour chaque instance (évite le piège de la liste mutable partagée)
- `__post_init__` : méthode appelée automatiquement après le `__init__` généré par dataclass, idéale pour les validations

---

### 🗄️ `app/persistence/repository.py` — Couche de persistance

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def add(self, obj): pass
    @abstractmethod
    def get(self, obj_id): pass
    @abstractmethod
    def get_all(self): pass
    @abstractmethod
    def update(self, obj_id, data): pass
    @abstractmethod
    def delete(self, obj_id): pass
    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value): pass
    @abstractmethod
    def get_all_by_attribute(self, attr_name, attr_value): pass


class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}    # dict { id: objet }

    def add(self, obj):
        self._storage[obj.id] = obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            obj.update(data)

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        return next(
            (obj for obj in self._storage.values()
             if getattr(obj, attr_name, None) == attr_value),
            None
        )

    def get_all_by_attribute(self, attr_name, attr_value):
        return [
            obj for obj in self._storage.values()
            if getattr(obj, attr_name, None) == attr_value
        ]
```

**Rôle :** Abstrait la persistance des données. Permet de remplacer le stockage en mémoire par une base de données sans toucher au reste du code (Part 3).

**Design Pattern : Repository Pattern**

```
HBnBFacade                Repository (ABC)
    |                           |
    |  utilise                  |  implémente
    ↓                           ↓
InMemoryRepository ←───── (futur: SQLAlchemyRepository)
```

**Classe `Repository` (ABC) :**

| Méthode abstraite | Signature | Rôle |
|-------------------|-----------|------|
| `add(obj)` | `obj` → None | Persiste un objet |
| `get(obj_id)` | `str` → obj \| None | Récupère par ID |
| `get_all()` | `()` → list | Retourne tous les objets |
| `update(obj_id, data)` | `str, dict` → None | Met à jour un objet |
| `delete(obj_id)` | `str` → bool | Supprime un objet |
| `get_by_attribute(attr, val)` | `str, any` → obj \| None | Recherche par attribut (ex: par email) |
| `get_all_by_attribute(attr, val)` | `str, any` → list | Tous les objets matchant |

**Classe `InMemoryRepository` :**

Le stockage interne `self._storage = {}` est un dictionnaire Python :
```python
{
    "3fa85f64-...": <User object>,
    "7b2c4a1d-...": <Place object>,
}
```

- **`get_by_attribute`** utilise `next()` avec un générateur pour trouver le premier objet correspondant. `getattr(obj, attr_name, None)` récupère l'attribut dynamiquement par son nom.
- **Limitation** : les données sont perdues au redémarrage du serveur (pas de base de données).

---

### 🎯 `app/services/facade.py` — Façade métier

```python
from app.models.entities import Amenity, Place, Review, User
from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ─── Users ────────────────────────────────────
    def create_user(self, user_data):
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

    # ─── Places ───────────────────────────────────
    def create_place(self, place_data):
        owner_id = place_data.get('owner_id')
        owner = self.get_user(owner_id)
        if not owner:
            raise ValueError('owner not found')
        # ...résolution des amenities IDs...
        from app.models.place import Place
        place = Place(title=..., owner=owner, ...)
        self.place_repo.add(place)
        return place

    # ─── Reviews ──────────────────────────────────
    def create_review(self, review_data):
        user = self.get_user(review_data.get('user_id'))
        if not user: raise ValueError('user not found')
        place = self.get_place(review_data.get('place_id'))
        if not place: raise ValueError('place not found')
        from app.models.review import Review
        review = Review(rating=..., comment=..., place=place, user=user)
        self.review_repo.add(review)
        return review

    def get_reviews_by_place(self, place_id):
        return [r for r in self.review_repo.get_all() if r.place.id == place_id]
```

**Rôle :** Interface unique entre les endpoints API et les données. Toute la **logique métier** est ici.

**Design Pattern : Facade Pattern**

```
API Layer          Facade           Repositories
  users.py  ──→               ──→  user_repo
  places.py ──→  HBnBFacade  ──→  place_repo
  reviews.py──→               ──→  review_repo
  amenities.py──→             ──→  amenity_repo
```

**Repositories par entité :**

| Repository | Contient | Type |
|------------|---------|------|
| `user_repo` | Objets `User` | `InMemoryRepository` |
| `place_repo` | Objets `Place` | `InMemoryRepository` |
| `review_repo` | Objets `Review` | `InMemoryRepository` |
| `amenity_repo` | Objets `Amenity` | `InMemoryRepository` |

**Méthodes CRUD complètes :**

| Ressource | Méthode Façade | Rôle |
|-----------|----------------|------|
| User | `create_user(data)` | Vérifie unicité email, hash password, persiste |
| User | `get_user(id)` | Récupère par ID |
| User | `get_users()` | Tous les utilisateurs |
| User | `update_user(id, data)` | Met à jour (email non modifiable) |
| Place | `create_place(data)` | Résout `owner_id` → User, amenity IDs → Amenity, valide, persiste |
| Place | `get_place(id)` | Récupère par ID |
| Place | `get_all_places()` | Tous les lieux |
| Place | `update_place(id, data)` | Met à jour |
| Amenity | `create_amenity(data)` | Crée et persiste |
| Amenity | `get_amenity(id)` | Récupère par ID |
| Amenity | `get_all_amenities()` | Toutes les amenities |
| Amenity | `update_amenity(id, data)` | Met à jour |
| Review | `create_review(data)` | Résout `user_id` et `place_id`, valide, persiste |
| Review | `get_review(id)` | Récupère par ID |
| Review | `get_all_reviews()` | Toutes les reviews |
| Review | `get_reviews_by_place(place_id)` | Reviews d'un lieu spécifique |
| Review | `update_review(id, data)` | Met à jour |
| Review | `delete_review(id)` | Supprime |

**Logique spéciale de `create_place` :**
```
1. Récupérer owner_id → chercher le User dans user_repo
   └→ Si introuvable : ValueError("owner not found")
2. Pour chaque ID dans amenity_ids → chercher l'Amenity dans amenity_repo
   └→ Si introuvable : ValueError(f"amenity {aid} not found")
3. Créer Place avec l'objet User owner (pas juste l'ID)
4. Ajouter chaque Amenity via place.add_amenity()
5. Persister dans place_repo
```

---

### 🔗 `app/services/__init__.py` — Singleton de la façade

```python
from app.services.facade import HBnBFacade

facade = HBnBFacade()
```

**Rôle :** Crée une **instance unique (singleton)** de `HBnBFacade` partagée par tous les endpoints.

**Pourquoi c'est important :**

```python
# Dans users.py :
from app.services import facade

# Dans places.py :
from app.services import facade

# Dans reviews.py :
from app.services import facade
```

Tous les endpoints importent **le même objet `facade`** → ils partagent les mêmes repositories → les données sont cohérentes entre les endpoints.

> Sans ce singleton, chaque endpoint aurait sa propre instance de `HBnBFacade` avec ses propres repositories vides → un User créé via `/api/v1/users/` serait invisible depuis `/api/v1/places/`.

---

### 📋 `app/api/__init__.py` — Blueprint API

```python
"""API v1 Blueprint — registers all namespaces."""
from flask import Blueprint
from flask_restx import Api
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.users import api as users_ns

blueprint = Blueprint("api_v1", __name__, url_prefix="/api/v1")
```

**Rôle :** Déclare le Blueprint Flask et importe tous les namespaces. Utilisé comme point de regroupement de l'API v1.

---

### 🛡️ `app/api/amenities.py` — Namespace Amenities alternatif

```python
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade

api = Namespace("amenities", description="Amenity management operations")
facade = HBnBFacade()   # Instance locale (différente du singleton)

amenity_input_model = api.model("AmenityInput", {
    "name": fields.String(required=True, example="Wi-Fi"),
})

amenity_output_model = api.model("Amenity", {
    "id": fields.String(),
    "name": fields.String(),
    "created_at": fields.String(),
    "updated_at": fields.String(),
})
```

**Rôle :** Version alternative et plus documentée du namespace Amenities. Contient des modèles d'entrée/sortie séparés et des exemples dans les champs Swagger.

> 📝 **Note :** Ce fichier (`app/api/amenities.py`) coexiste avec `app/api/v1/amenities.py`. C'est la version `v1` qui est enregistrée dans `create_app()`. Ce fichier est une version de référence/documentation pédagogique.

---

### 👥 `app/api/v1/users.py` — Endpoints utilisateurs

```python
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='Operations on users')

# Modèles de validation / documentation Swagger
user_model = api.model('User', {
    'id': fields.String(readonly=True),
    'email': fields.String(required=True),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'created_at': fields.String(readonly=True),
    'updated_at': fields.String(readonly=True),
})
create_user_model = api.model('UserCreate', {
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
})
update_user_model = api.model('UserUpdate', {
    'first_name': fields.String(),
    'last_name': fields.String(),
    'password': fields.String(),
})
```

**Rôle :** Définit tous les endpoints HTTP pour la ressource User.

**Routes exposées :**

| Méthode | URL | Description | Codes retour |
|---------|-----|-------------|--------------|
| `GET` | `/api/v1/users/` | Liste tous les utilisateurs | `200` |
| `POST` | `/api/v1/users/` | Crée un nouvel utilisateur | `201`, `400`, `409` |
| `GET` | `/api/v1/users/<user_id>` | Récupère un utilisateur par ID | `200`, `404` |
| `PUT` | `/api/v1/users/<user_id>` | Met à jour un utilisateur | `200`, `404` |

**Classes Resource :**

```
UserList    ← /api/v1/users/
  └── GET  → facade.get_users()          → liste de dicts
  └── POST → facade.create_user(data)    → dict ou erreur

UserResource ← /api/v1/users/<user_id>
  └── GET  → facade.get_user(user_id)    → dict ou 404
  └── PUT  → facade.update_user(id, data)→ dict ou 404
```

**Gestion des erreurs `POST` :**

```python
try:
    user = facade.create_user(data)
except ValueError as e:
    msg = str(e)
    if 'in use' in msg:
        return {'message': msg}, 409   # Email déjà utilisé
    return {'message': msg}, 400       # Autre erreur de validation
return user.to_dict(), 201
```

| Erreur | Code HTTP | Raison |
|--------|-----------|--------|
| Email manquant | `400` | Bad Request |
| Email invalide | `400` | Bad Request |
| Email déjà utilisé | `409` | Conflict |
| Création OK | `201` | Created |

**Décorateurs Flask-RESTX :**

| Décorateur | Rôle |
|------------|------|
| `@api.route('/')` | Lie la classe Resource à l'URL |
| `@api.expect(model)` | Valide le corps de la requête selon le modèle |
| `@api.marshal_with(model)` | Filtre/formate la réponse selon le modèle |
| `@api.response(code, desc)` | Documente un code de réponse possible dans Swagger |
| `@api.param('id', 'desc')` | Documente un paramètre d'URL dans Swagger |

---

### 🏊 `app/api/v1/amenities.py` — Endpoints équipements

```python
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'id': fields.String(readonly=True),
    'name': fields.String(required=True, description='Amenity name (max 50 chars)'),
    'description': fields.String(),
    'created_at': fields.String(readonly=True),
    'updated_at': fields.String(readonly=True),
})
```

**Rôle :** Endpoints HTTP pour la ressource Amenity.

**Routes exposées :**

| Méthode | URL | Description | Codes retour |
|---------|-----|-------------|--------------|
| `GET` | `/api/v1/amenities/` | Liste toutes les amenities | `200` |
| `POST` | `/api/v1/amenities/` | Crée une amenity | `201`, `400` |
| `GET` | `/api/v1/amenities/<amenity_id>` | Récupère par ID | `200`, `404` |
| `PUT` | `/api/v1/amenities/<amenity_id>` | Met à jour | `200`, `400`, `404` |

**Particularité `validate=True` :**
```python
@api.expect(create_amenity_model, validate=True)
```
Avec `validate=True`, Flask-RESTX rejette automatiquement les requêtes dont le corps ne correspond pas au modèle **avant même** d'entrer dans la méthode. Sans `validate=True`, la validation doit être faite manuellement.

---

### 🏠 `app/api/v1/places.py` — Endpoints lieux

```python
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Place operations')

place_model = api.model('Place', {
    'title': fields.String(required=True),
    'description': fields.String(),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'owner_id': fields.String(required=True),
    'amenities': fields.List(fields.String, required=False)
})
```

**Rôle :** Endpoints HTTP pour la ressource Place.

**Routes exposées :**

| Méthode | URL | Description | Codes retour |
|---------|-----|-------------|--------------|
| `GET` | `/api/v1/places/` | Liste tous les lieux (résumé) | `200` |
| `POST` | `/api/v1/places/` | Crée un lieu | `201`, `400`, `501` |
| `GET` | `/api/v1/places/<place_id>` | Détail complet + owner + amenities | `200`, `404` |
| `PUT` | `/api/v1/places/<place_id>` | Met à jour | `200`, `400`, `404` |

**Réponses différentes selon le contexte :**

`GET /api/v1/places/` (liste) retourne un résumé :
```json
[
  {"id": "abc", "title": "Belle villa", "latitude": 48.85, "longitude": 2.35}
]
```

`GET /api/v1/places/<id>` (détail) retourne tout :
```json
{
  "id": "abc",
  "title": "Belle villa",
  "price": 150.0,
  "owner": {"id": "xyz", "first_name": "Alice", "last_name": "Smith", "email": "alice@ex.com"},
  "amenities": [{"id": "wifi1", "name": "Wi-Fi"}]
}
```

**Gestion `getattr` pour la robustesse :**
```python
create_place_fn = getattr(facade, "create_place", None)
if create_place_fn is None:
    return {'error': 'Place creation not implemented in service layer'}, 501
```
`getattr(facade, "create_place", None)` cherche la méthode `create_place` sur l'objet `facade`. Si elle n'existe pas, retourne `None` au lieu de lever une `AttributeError`. Code `501 Not Implemented` retourné si la fonctionnalité manque.

---

### ✍️ `app/api/v1/reviews.py` — Endpoints avis

```python
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('reviews', description='Review operations')
```

**Rôle :** Endpoints HTTP pour la ressource Review. Le seul endpoint qui implémente **DELETE**.

**Routes exposées :**

| Méthode | URL | Description | Codes retour |
|---------|-----|-------------|--------------|
| `GET` | `/api/v1/reviews/` | Liste toutes les reviews | `200` |
| `POST` | `/api/v1/reviews/` | Crée une review | `201`, `400`, `404` |
| `GET` | `/api/v1/reviews/<review_id>` | Récupère par ID | `200`, `404` |
| `PUT` | `/api/v1/reviews/<review_id>` | Met à jour | `200`, `400`, `404` |
| `DELETE` | `/api/v1/reviews/<review_id>` | Supprime | `200`, `404` |
| `GET` | `/api/v1/reviews/places/<place_id>/reviews` | Toutes les reviews d'un lieu | `200`, `404` |

**Gestion d'erreur `POST` (404 vs 400) :**
```python
try:
    review = facade.create_review(api.payload)
except ValueError as e:
    msg = str(e)
    if 'not found' in msg:
        return {'message': msg}, 404   # User ou Place introuvable
    return {'message': msg}, 400       # Données invalides
```

**Endpoint `DELETE` :**
```python
def delete(self, review_id):
    review = facade.get_review(review_id)
    if not review:
        api.abort(404, 'Review not found')
    facade.delete_review(review_id)
    return {'message': 'Review deleted successfully'}, 200
```
1. Vérifie que la review existe (404 si non)
2. Supprime via la façade
3. Retourne confirmation 200

**Route imbriquée (nested route) :**
```python
@api.route('/places/<string:place_id>/reviews')
class PlaceReviewList(Resource):
    def get(self, place_id):
        """Get all reviews for a specific place"""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')
        return [r.to_dict() for r in facade.get_reviews_by_place(place_id)], 200
```
Cette route imbriquée suit la convention REST : `/reviews/places/<id>/reviews` donne toutes les reviews d'un lieu précis.

---

### 🧪 `app/tests/test_models.py` — Tests unitaires modèles

```python
"""Unit tests for model validation logic (no network / no Flask required)."""
import unittest
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
```

**Rôle :** 43 tests unitaires qui vérifient la logique de validation des modèles, **sans démarrer Flask ni faire de requêtes HTTP**.

**Structure des tests (helpers) :**
```python
def make_user(**kwargs):
    """Crée un User valide avec des valeurs par défaut overridables"""
    defaults = {'first_name': 'John', 'last_name': 'Doe',
                'email': 'john@example.com', 'password': 'secret123'}
    defaults.update(kwargs)
    return User(**defaults)
```

**Couverture des tests :**

| Classe | Nombre de tests | Ce qui est testé |
|--------|----------------|------------------|
| `TestUserModel` | 13 | Création valide, hachage password, to_dict sans password, validations champs, is_admin |
| `TestPlaceModel` | 15 | Création valide, titre/prix/lat/long, owner requis, add_amenity, rating moyen, to_dict |
| `TestReviewModel` | 10 | Création valide, comment vide, rating 0/6/float, limites 1 et 5, place/user None, to_dict |
| `TestAmenityModel` | 5 | Création valide, description, nom vide, nom trop long, to_dict |

**Exemple de test :**
```python
def test_password_is_hashed(self):
    user = make_user(password='mypassword')
    self.assertNotEqual(user.password_hash, 'mypassword')  # Hash ≠ clair
    self.assertTrue(user.authenticate('mypassword'))        # Auth OK
    self.assertFalse(user.authenticate('wrongpassword'))    # Mauvais MDP
```

---

### 🌐 `app/tests/test_api.py` — Tests API utilisateurs

```python
import unittest
from app import create_app

class UsersAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
```

**Rôle :** Tests de l'API Users en utilisant le client de test Flask.

**`setUp()` :** Appelée avant chaque test. Crée une nouvelle app Flask fraîche et un client HTTP de test.

**Tests inclus :**

| Test | Ce qui est vérifié |
|------|-------------------|
| `test_user_crud_flow` | Création (201), listage (200), récupération par ID (200), mise à jour (200), 404 sur ID inconnu |
| `test_duplicate_email` | Premier POST → 201, second POST même email → 409 |

**Vérifications importantes :**
```python
# Le password ne doit jamais apparaître dans la réponse
self.assertNotIn('password', data)

# L'ID doit être dans la réponse
self.assertIn('id', data)
```

---

### 🏊 `app/tests/test_amenities.py` — Tests API Amenities

```python
import unittest
from app import create_app

class AmenitiesAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
```

**Rôle :** Tests du cycle CRUD complet de l'API Amenities.

**Utilise `create_app("testing")`** : charge la `TestingConfig` avec `TESTING=True`, ce qui permet aux exceptions de remonter proprement dans les tests.

**Flux testé :**
1. `POST /api/v1/amenities/` avec `{"name": "Wi-Fi"}` → `201`
2. `GET /api/v1/amenities/` → `200`, vérifie que Wi-Fi est dans la liste
3. `PUT /api/v1/amenities/<id>` avec `{"name": "Parking"}` → `200`, vérifie le nouveau nom
4. `GET /api/v1/amenities/<id>` → `200`, vérifie l'ID

---

### 🔬 `app/tests/test_endpoint.py` — Tests d'intégration complets

```python
"""Integration tests for all API endpoints (Users, Places, Amenities, Reviews)."""
import unittest
import uuid
from app import create_app

def _unique_email(prefix='user'):
    return f'{prefix}_{uuid.uuid4().hex[:8]}@test.com'

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def _create_user(self, email=None, ...):
        ...
    def _create_amenity(self, name='Wi-Fi'):
        ...
    def _create_place(self, owner_id, amenity_ids=None, **overrides):
        ...
    def _create_review(self, user_id, place_id, ...):
        ...
```

**Rôle :** 36 tests d'intégration couvrant **tous** les endpoints avec des scénarios réalistes.

**`_unique_email()`** : génère des emails uniques pour éviter les conflits entre tests (chaque test crée sa propre app, mais certains tests dans la même classe partagent l'état).

**Classes de tests :**

| Classe | Tests | Endpoints couverts |
|--------|-------|-------------------|
| `TestAmenityEndpoints` | 8 | CRUD Amenities + cas d'erreur |
| `TestPlaceEndpoints` | 10 | CRUD Places + validations géo + amenities |
| `TestReviewEndpoints` | 10 | CRUD Reviews + DELETE + reviews par place |
| `TestUserEndpoints` | 8 | CRUD Users + email dupliqué |

**Scénario place avec amenity :**
```python
def test_create_place_with_amenity(self):
    amenity_id = self._create_amenity('Sauna').get_json()['id']
    resp = self._create_place(self.owner_id, amenity_ids=[amenity_id])
    self.assertEqual(resp.status_code, 201)
```
Ce test vérifie l'intégration complète : créer une amenity, créer un lieu qui référence cette amenity.

---

### 📊 `app/tests/tests_report.md` — Rapport de tests

**Rôle :** Documentation complète des résultats de tests et des règles de validation implémentées.

**Résultats globaux :**

| Suite de tests | Tests | Passés | Échoués |
|---------------|-------|--------|---------|
| `test_api.py` | 2 | ✅ 2 | 0 |
| `test_models.py` | 43 | ✅ 43 | 0 |
| `test_endpoint.py` | 36 | ✅ 36 | 0 |
| **TOTAL** | **81** | **✅ 81** | **0** |

---

### 🐚 `curl_tests.sh` — Tests manuels cURL

```bash
#!/bin/bash
BASE="http://127.0.0.1:5000/api/v1"

# Test 1 : Créer un utilisateur (201)
curl -s -X POST "$BASE/users/" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123","first_name":"Alice","last_name":"Smith"}' \
  | python3 -m json.tool
```

**Rôle :** Script bash qui teste manuellement **tous les endpoints** via cURL. Utile pour tester rapidement l'API sans framework de test.

**Nombre de tests :** ~35+ appels couvrant Users, Amenities, Places et Reviews.

**Utilisation :**
```bash
# 1. Démarrer le serveur
python run.py

# 2. Dans un autre terminal
bash curl_tests.sh
```

**Techniques utilisées :**
```bash
# Capturer l'ID retourné par une requête pour l'utiliser dans la suivante
USER_ID=$(curl -s -X POST "$BASE/users/" \
  -H "Content-Type: application/json" \
  -d '{...}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

`python3 -m json.tool` : formate le JSON pour le rendre lisible dans le terminal.

---

## 🎨 Patterns architecturaux

### 1. Factory Pattern (`create_app`)

```python
# On peut créer différentes apps selon le contexte
app_dev  = create_app('development')
app_test = create_app('testing')
app_prod = create_app('production')
```

### 2. Facade Pattern (`HBnBFacade`)

```
API → Facade → Repositories
```
La Facade unifie l'accès aux 4 repositories derrière une interface simple.

### 3. Repository Pattern (`InMemoryRepository`)

```
Code métier → Repository (interface) → Storage (dict, DB, etc.)
```
Découple la logique métier de la persistance. En Part 3, on remplacera `InMemoryRepository` par `SQLAlchemyRepository` sans toucher au reste.

### 4. Singleton (`app/services/__init__.py`)

```python
facade = HBnBFacade()  # Une seule instance partagée
```

### 5. Template Method (héritage des modèles)

```
BaseModel.to_dict()         ← méthode de base
User.to_dict() → super()    ← extension
Place.to_dict() → super()   ← extension
```

---

## 📐 Modèles de données & validations

### User

```
User
├── id           : UUID (auto)
├── created_at   : datetime (auto)
├── updated_at   : datetime (auto)
├── first_name   : str (requis, max 50)
├── last_name    : str (requis, max 50)
├── email        : str (requis, format local@domain.tld, UNIQUE)
├── password_hash: str (SHA256, JAMAIS exposé en JSON)
└── is_admin     : bool (défaut False)
```

### Place

```
Place
├── id           : UUID (auto)
├── created_at   : datetime (auto)
├── updated_at   : datetime (auto)
├── title        : str (requis, max 100)
├── description  : str (optionnel)
├── price        : float (> 0)
├── latitude     : float ([-90, 90])
├── longitude    : float ([-180, 180])
├── owner        : User (requis, objet)
├── max_guests   : int (>= 1, défaut 1)
├── is_available : bool (défaut True)
├── reviews      : list[Review] (initialisé vide)
└── amenities    : list[Amenity] (initialisé vide)
```

### Amenity

```
Amenity
├── id          : UUID (auto)
├── created_at  : datetime (auto)
├── updated_at  : datetime (auto)
├── name        : str (requis, max 50)
└── description : str (optionnel, défaut "")
```

### Review

```
Review
├── id        : UUID (auto)
├── created_at: datetime (auto)
├── updated_at: datetime (auto)
├── rating    : int (1 ≤ n ≤ 5, entier strict)
├── comment   : str (requis, non vide)
├── place     : Place (requis, objet)
└── user      : User (requis, objet)
```

---

## 🌐 Endpoints de l'API

### Users — `/api/v1/users/`

| Méthode | URL | Corps | Retour | Codes |
|---------|-----|-------|--------|-------|
| `GET` | `/api/v1/users/` | — | `[{user}, ...]` | 200 |
| `POST` | `/api/v1/users/` | `{email, password, first_name, last_name}` | `{user}` | 201, 400, 409 |
| `GET` | `/api/v1/users/<id>` | — | `{user}` | 200, 404 |
| `PUT` | `/api/v1/users/<id>` | `{first_name?, last_name?, password?}` | `{user}` | 200, 404 |

### Places — `/api/v1/places/`

| Méthode | URL | Corps | Retour | Codes |
|---------|-----|-------|--------|-------|
| `GET` | `/api/v1/places/` | — | `[{id,title,lat,lon}, ...]` | 200 |
| `POST` | `/api/v1/places/` | `{title, price, latitude, longitude, owner_id, amenities?}` | `{place}` | 201, 400 |
| `GET` | `/api/v1/places/<id>` | — | `{place + owner + amenities}` | 200, 404 |
| `PUT` | `/api/v1/places/<id>` | `{champs modifiables}` | `{message}` | 200, 400, 404 |

### Amenities — `/api/v1/amenities/`

| Méthode | URL | Corps | Retour | Codes |
|---------|-----|-------|--------|-------|
| `GET` | `/api/v1/amenities/` | — | `[{amenity}, ...]` | 200 |
| `POST` | `/api/v1/amenities/` | `{name, description?}` | `{amenity}` | 201, 400 |
| `GET` | `/api/v1/amenities/<id>` | — | `{amenity}` | 200, 404 |
| `PUT` | `/api/v1/amenities/<id>` | `{name?, description?}` | `{amenity}` | 200, 400, 404 |

### Reviews — `/api/v1/reviews/`

| Méthode | URL | Corps | Retour | Codes |
|---------|-----|-------|--------|-------|
| `GET` | `/api/v1/reviews/` | — | `[{review}, ...]` | 200 |
| `POST` | `/api/v1/reviews/` | `{rating, comment, user_id, place_id}` | `{review}` | 201, 400, 404 |
| `GET` | `/api/v1/reviews/<id>` | — | `{review}` | 200, 404 |
| `PUT` | `/api/v1/reviews/<id>` | `{rating?, comment?}` | `{review}` | 200, 400, 404 |
| `DELETE` | `/api/v1/reviews/<id>` | — | `{message}` | 200, 404 |
| `GET` | `/api/v1/reviews/places/<place_id>/reviews` | — | `[{review}, ...]` | 200, 404 |

---

## 🔄 Flux de données

### Exemple : Créer une Review

```
Client
  │
  │ POST /api/v1/reviews/
  │ {"rating":4,"comment":"Super!","user_id":"u1","place_id":"p1"}
  ↓
reviews.py (ReviewList.post)
  │ api.payload → {"rating":4,"comment":"Super!","user_id":"u1","place_id":"p1"}
  │ facade.create_review(payload)
  ↓
facade.py (HBnBFacade.create_review)
  │ user_repo.get("u1") → User object ou None
  │ place_repo.get("p1") → Place object ou None
  │ Review(rating=4, comment="Super!", place=Place, user=User)
  │ review_repo.add(review)
  ↓
repository.py (InMemoryRepository.add)
  │ _storage["review_id"] = review
  ↓
review.to_dict() → {"id":"r1","rating":4,"comment":"Super!","place_id":"p1","user_id":"u1",...}
  ↓
Client reçoit 201 + JSON
```

### Exemple : Erreur de validation

```
Client POST /api/v1/reviews/
{"rating":6,"comment":"test","user_id":"u1","place_id":"p1"}
          ↓
reviews.py → facade.create_review(data)
          ↓
Review.__init__(rating=6, ...)
  → not 1 <= 6 <= 5 → True
  → raise ValueError("rating must be an integer between 1 and 5")
          ↓
facade.create_review attrape ValueError → re-raise
          ↓
reviews.py attrape ValueError
  → return {'message': 'rating must be an integer between 1 and 5'}, 400
          ↓
Client reçoit 400 + {"message": "rating must be an integer between 1 and 5"}
```

---

## 🚀 Lancer le projet

### Prérequis

```bash
python3 --version  # Python 3.8+
pip --version
```

### Installation

```bash
# Se placer dans le dossier part2
cd holbertonschool-hbnb/part2

# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou : venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Démarrer le serveur

```bash
python run.py
```

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Accéder à la documentation Swagger

```
http://127.0.0.1:5000/doc
```

La documentation Swagger est auto-générée par Flask-RESTX. Elle permet de :
- Voir tous les endpoints disponibles
- Lire les modèles de données attendus
- Tester les requêtes directement dans le navigateur

---

## 🧪 Lancer les tests

### Tous les tests (recommandé)

```bash
python -m unittest discover -s app/tests -v
```

### Tests spécifiques

```bash
# Tests unitaires des modèles uniquement
python -m unittest app/tests/test_models.py -v

# Tests de l'API Users
python -m unittest app/tests/test_api.py -v

# Tests intégration complets
python -m unittest app/tests/test_endpoint.py -v
```

### Tests manuels cURL

```bash
# Démarrer le serveur dans un terminal
python run.py

# Dans un autre terminal
bash curl_tests.sh
```

### Résultat attendu

```
Ran 81 tests in X.XXXs

OK
```

---

## 📊 Récapitulatif des validations

| Modèle | Champ | Règle | Erreur levée |
|--------|-------|-------|-------------|
| User | `first_name` | Requis, max 50 chars | `ValueError` |
| User | `last_name` | Requis, max 50 chars | `ValueError` |
| User | `email` | Format `local@domain.tld`, UNIQUE | `ValueError` |
| User | `password` | Requis, non vide | `ValueError` |
| Place | `title` | Requis, max 100 chars | `ValueError` |
| Place | `price` | Strictement positif (> 0) | `ValueError` |
| Place | `latitude` | Entre -90 et +90 | `ValueError` |
| Place | `longitude` | Entre -180 et +180 | `ValueError` |
| Place | `owner` | Instance de User, non None | `ValueError` |
| Amenity | `name` | Requis, max 50 chars | `ValueError` |
| Review | `comment` | Requis, non vide | `ValueError` |
| Review | `rating` | Entier strict entre 1 et 5 | `ValueError` |
| Review | `place` | Instance de Place, non None | `ValueError` |
| Review | `user` | Instance de User, non None | `ValueError` |

---

*README généré pour HBnB Part 2 — Holberton School*
