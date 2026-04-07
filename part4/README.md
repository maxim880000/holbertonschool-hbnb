# 🏠 HBnB — Part 3 : Authentication, Authorization & Database Persistence

> **Holberton School** — Projet HBnB (AirBnB Clone)
> **Part 3** : Ajout de l'authentification JWT, du hachage de mot de passe bcrypt, du contrôle d'accès par rôle (admin/user), et de la persistance SQLAlchemy avec SQLite.

---

## 📋 Table des matières

1. [Vue d'ensemble du projet](#-vue-densemble-du-projet)
2. [Nouveautés Part 3](#-nouveautés-part-3)
3. [Architecture globale](#-architecture-globale)
4. [Arborescence annotée](#-arborescence-annotée)
5. [Tableau complet des fichiers](#-tableau-complet-des-fichiers)
6. [Modèles de données & relations](#-modèles-de-données--relations)
7. [Endpoints de l'API](#-endpoints-de-lapi)
8. [Authentification & Autorisations](#-authentification--autorisations)
9. [Lancer le projet](#-lancer-le-projet)
10. [Lancer les tests](#-lancer-les-tests)
11. [Diagramme ER](#-diagramme-er)

---

## 🌍 Vue d'ensemble du projet

HBnB Part 3 est une **API REST sécurisée** qui simule le backend d'une plateforme de location de logements (style AirBnB). Elle expose 4 ressources principales accessibles via HTTP, protégées par **JWT** avec gestion des rôles **admin / utilisateur**.

| Ressource     | Description                                     | Endpoint de base        |
|---------------|-------------------------------------------------|-------------------------|
| **Users**     | Utilisateurs (propriétaires et locataires)      | `/api/v1/users/`        |
| **Places**    | Logements disponibles à la location             | `/api/v1/places/`       |
| **Amenities** | Équipements disponibles dans les logements      | `/api/v1/amenities/`    |
| **Reviews**   | Avis laissés par des utilisateurs sur des lieux | `/api/v1/reviews/`      |

**Technologies utilisées :**

| Package | Rôle |
|---------|------|
| `flask` | Framework web |
| `flask-restx` | Extensions REST + Swagger auto |
| `flask-sqlalchemy` | ORM SQLAlchemy pour Flask |
| `flask-bcrypt` | Hachage des mots de passe bcrypt |
| `flask-jwt-extended` | Authentification JWT |
| `pytest` | Suite de tests automatisés |

---

## 🆕 Nouveautés Part 3

| # | Tâche | Description |
|---|-------|-------------|
| 3-0 | Application Factory | Intégration SQLAlchemy + Bcrypt + JWT dans `create_app()` |
| 3-1 | Password Hashing | Mots de passe hachés avec bcrypt (jamais stockés en clair) |
| 3-2 | JWT Authentication | Login → token JWT, endpoints protégés par `@jwt_required()` |
| 3-3 | Authenticated User Access | Users ne peuvent modifier que leurs propres ressources |
| 3-4 | Administrator Access | Admins peuvent tout modifier, rôle `is_admin` dans le JWT |
| 3-5 | SQLAlchemy Repository | `SQLAlchemyRepository` remplace `InMemoryRepository` pour les Users |
| 3-6 | Map User Entity | `User` devient un modèle SQLAlchemy (`db.Model`) |
| 3-7 | Map Place/Review/Amenity | Tous les modèles mappés en SQLAlchemy |
| 3-8 | Map Relationships | Relations `one-to-many` et `many-to-many` via SQLAlchemy |
| 3-9 | SQL Scripts | Scripts SQL de création des tables et données initiales |
| 3-10 | ER Diagram | Diagramme entité-relation en Mermaid.js (`ER_diagram.md`) |

---

## 🏛️ Architecture globale

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Swagger / curl)                  │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP Request
┌────────────────────────────▼────────────────────────────────┐
│              COUCHE API  (app/api/v1/*.py)                  │
│   Flask-RESTX Namespaces • Validation • Swagger UI /doc     │
│   @jwt_required() • get_jwt() • get_jwt_identity()          │
└────────────────────────────┬────────────────────────────────┘
                             │ appelle
┌────────────────────────────▼────────────────────────────────┐
│           COUCHE SERVICE  (app/services/facade.py)          │
│   HBnBFacade • Logique métier • Résolution des IDs          │
│   Validation des droits d'accès                             │
└────────────────────────────┬────────────────────────────────┘
                             │ appelle
┌────────────────────────────▼────────────────────────────────┐
│       COUCHE PERSISTANCE  (app/persistence/)                │
│   SQLAlchemyRepository (Users) + InMemoryRepository         │
│   (Places / Reviews / Amenities)                            │
└────────────────────────────┬────────────────────────────────┘
                             │ retourne des objets
┌────────────────────────────▼────────────────────────────────┐
│           COUCHE MODÈLES  (app/models/*.py)                 │
│   User • Place • Amenity • Review • BaseModel               │
│   SQLAlchemy db.Model • Validation • Sérialisation JSON     │
└─────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   BASE DE DONNÉES SQLite                    │
│   development.db (dev) • :memory: (tests)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Arborescence annotée

```
part3/
│
├── run.py                          ← DÉMARRER LE SERVEUR ICI
├── config.py                       ← Config multi-env racine (non utilisée)
├── requirements.txt                ← Dépendances Python
├── ER_diagram.md                   ← Diagramme ER Mermaid.js
│
└── app/
    ├── __init__.py                 ← create_app() : factory Flask + SQLAlchemy + JWT + Bcrypt
    ├── config.py                   ← DevelopmentConfig / TestingConfig / ProductionConfig
    │
    ├── api/
    │   ├── __init__.py
    │   ├── amenities.py            ← Namespace amenities alternatif
    │   └── v1/
    │       ├── __init__.py
    │       ├── users.py            ← CRUD Users + login + JWT
    │       ├── places.py           ← CRUD Places + contrôle propriétaire
    │       ├── amenities.py        ← CRUD Amenities (admin only pour POST/PUT)
    │       └── reviews.py          ← CRUD Reviews + contrôle auteur
    │
    ├── models/
    │   ├── __init__.py
    │   ├── base_model.py           ← BaseModel(db.Model) : id UUID, timestamps
    │   ├── user.py                 ← User : bcrypt hash, verify_password()
    │   ├── place.py                ← Place : FK owner_id, many-to-many amenities
    │   ├── amenity.py              ← Amenity : name unique max 50 chars
    │   ├── review.py               ← Review : FK user_id + place_id, rating 1-5
    │   └── entities.py             ← Entités dataclass (legacy)
    │
    ├── persistence/
    │   ├── __init__.py
    │   ├── repository.py           ← ABC Repository + InMemoryRepository + SQLAlchemyRepository
    │   └── sqlalchemy_repository.py ← (alias/extension SQLAlchemy)
    │
    ├── services/
    │   ├── __init__.py             ← facade = HBnBFacade() singleton
    │   ├── facade.py               ← HBnBFacade : CRUD complet + logique métier
    │   └── repositories/
    │       ├── __init__.py
    │       └── user_repository.py  ← UserRepository(SQLAlchemyRepository) + get_user_by_email()
    │
    └── tests/
        ├── test_models.py          ← Tests unitaires modèles
        ├── test_api.py             ← Tests CRUD Users (ancien)
        ├── test_amenities.py       ← Tests CRUD Amenities (ancien)
        ├── test_endpoint.py        ← Tests intégration (ancien)
        └── test_part3_full.py      ← 50 tests complets Part 3 (auth + CRUD + accès)
```

---

## 📁 Tableau complet des fichiers

| # | Chemin | Rôle |
|---|--------|------|
| 1 | `run.py` | Point d'entrée — lance le serveur Flask |
| 2 | `app/__init__.py` | Factory Flask : init SQLAlchemy, Bcrypt, JWT, namespaces |
| 3 | `app/config.py` | Configs Development / Testing / Production |
| 4 | `app/models/base_model.py` | Classe de base SQLAlchemy : `id`, `created_at`, `updated_at` |
| 5 | `app/models/user.py` | User : bcrypt hash, `verify_password()`, `to_dict()` sans password |
| 6 | `app/models/place.py` | Place : FK `owner_id`, relation many-to-many `amenities` |
| 7 | `app/models/amenity.py` | Amenity : `name` unique, max 50 chars |
| 8 | `app/models/review.py` | Review : FK `user_id` + `place_id`, rating 1-5 |
| 9 | `app/persistence/repository.py` | `InMemoryRepository` + `SQLAlchemyRepository` |
| 10 | `app/services/repositories/user_repository.py` | `UserRepository` avec `get_user_by_email()` |
| 11 | `app/services/facade.py` | `HBnBFacade` : toute la logique métier |
| 12 | `app/api/v1/users.py` | Endpoints users + login + `/me` |
| 13 | `app/api/v1/places.py` | Endpoints places + contrôle propriétaire |
| 14 | `app/api/v1/amenities.py` | Endpoints amenities (admin only write) |
| 15 | `app/api/v1/reviews.py` | Endpoints reviews + contrôle auteur |
| 16 | `app/tests/test_part3_full.py` | **50 tests** couvrant auth, users, places, reviews, amenities |
| 17 | `ER_diagram.md` | Diagramme ER Mermaid.js de la base de données |

---

## 🗄️ Modèles de données & relations

### Tables

| Table | Colonnes principales | Relations |
|-------|---------------------|-----------|
| `users` | `id`, `first_name`, `last_name`, `email`, `password` (hash), `is_admin` | → places, → reviews |
| `places` | `id`, `title`, `description`, `price`, `latitude`, `longitude`, `owner_id` (FK) | → owner, → reviews, ↔ amenities |
| `reviews` | `id`, `text`, `rating`, `user_id` (FK), `place_id` (FK) | → user, → place |
| `amenities` | `id`, `name`, `description` | ↔ places |
| `place_amenity` | `place_id` (FK), `amenity_id` (FK) | table d'association many-to-many |

### Relations

| Relation | Type | Description |
|----------|------|-------------|
| User → Place | One-to-Many | Un user peut posséder plusieurs places |
| User → Review | One-to-Many | Un user peut écrire plusieurs reviews |
| Place → Review | One-to-Many | Une place peut avoir plusieurs reviews |
| Place ↔ Amenity | Many-to-Many | Via la table `place_amenity` |

---

## 🔌 Endpoints de l'API

### Users

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `GET` | `/api/v1/users/` | Non | Liste tous les users |
| `POST` | `/api/v1/users/` | Admin (sauf 1er) | Crée un user |
| `GET` | `/api/v1/users/<id>` | Non | Récupère un user |
| `PUT` | `/api/v1/users/<id>` | JWT (soi-même ou admin) | Modifie un user |
| `POST` | `/api/v1/users/login` | Non | Retourne un token JWT |
| `GET` | `/api/v1/users/me` | JWT | Retourne l'identité du token |

### Places

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `GET` | `/api/v1/places/` | Non | Liste toutes les places |
| `POST` | `/api/v1/places/` | JWT (owner) | Crée une place |
| `GET` | `/api/v1/places/<id>` | Non | Détails d'une place (owner + amenities) |
| `PUT` | `/api/v1/places/<id>` | JWT (owner ou admin) | Modifie une place |
| `DELETE` | `/api/v1/places/<id>` | JWT (owner ou admin) | Supprime une place |

### Amenities

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `GET` | `/api/v1/amenities/` | Non | Liste toutes les amenities |
| `POST` | `/api/v1/amenities/` | Admin | Crée une amenity |
| `GET` | `/api/v1/amenities/<id>` | Non | Récupère une amenity |
| `PUT` | `/api/v1/amenities/<id>` | Admin | Modifie une amenity |

### Reviews

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `GET` | `/api/v1/reviews/` | Non | Liste tous les reviews |
| `POST` | `/api/v1/reviews/` | JWT (auteur) | Crée un review |
| `GET` | `/api/v1/reviews/<id>` | Non | Récupère un review |
| `PUT` | `/api/v1/reviews/<id>` | JWT (auteur ou admin) | Modifie un review |
| `DELETE` | `/api/v1/reviews/<id>` | JWT (auteur ou admin) | Supprime un review |
| `GET` | `/api/v1/reviews/places/<id>/reviews` | Non | Reviews d'une place |

---

## 🔐 Authentification & Autorisations

### Flux d'authentification

```
1. POST /api/v1/users/login  →  { "access_token": "eyJ..." }
2. Copier le token
3. Ajouter dans les headers : Authorization: Bearer <token>
4. Accéder aux endpoints protégés
```

### Règles d'accès

| Action | Utilisateur non connecté | Utilisateur connecté | Admin |
|--------|--------------------------|----------------------|-------|
| Créer un user | ✅ (1er user seulement) | ❌ | ✅ |
| Modifier son profil | ❌ | ✅ (nom/prénom uniquement) | ✅ (tout) |
| Modifier le profil d'un autre | ❌ | ❌ | ✅ |
| Créer une place | ❌ | ✅ (owner_id = soi) | ✅ |
| Modifier/supprimer sa place | ❌ | ✅ | ✅ |
| Créer une amenity | ❌ | ❌ | ✅ |
| Créer un review | ❌ | ✅ (user_id = soi) | ✅ |
| Modifier/supprimer son review | ❌ | ✅ | ✅ |

### Premier démarrage

Le **premier utilisateur créé** devient automatiquement admin (`is_admin = True`). Tous les suivants nécessitent un token admin.

---

## 🚀 Lancer le projet

```bash
# 1. Cloner le repo et naviguer dans part3
cd part3

# 2. Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le serveur
python run.py
```

- **API** : `http://localhost:5000/api/v1/`
- **Swagger UI** : `http://localhost:5000/doc`

---

## 🧪 Lancer les tests

```bash
cd part3
python -m pytest app/tests/test_part3_full.py -v
```

### Résultats attendus

```
50 passed in ~38s
```

| Catégorie | Tests | Description |
|-----------|-------|-------------|
| Authentification | 5 | Login, token invalide, /me |
| Users | 11 | CRUD, contrôle d'accès, password non exposé |
| Places | 13 | CRUD, contrôle propriétaire, validations |
| Reviews | 13 | CRUD, contrôle auteur, validations |
| Amenities | 8 | CRUD, admin only |
| **Total** | **50** | |

---

## 📊 Diagramme ER

Le diagramme entité-relation complet est disponible dans [`ER_diagram.md`](./ER_diagram.md).

Il représente les 5 tables (`USER`, `PLACE`, `REVIEW`, `AMENITY`, `PLACE_AMENITY`) et leurs relations, généré avec Mermaid.js.

> Visualisable directement sur GitHub ou sur [mermaid.live](https://mermaid.live).
