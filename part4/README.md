# 🏠 HBnB — Part 4 : Frontend Web Application

> **Holberton School** — Projet HBnB (AirBnB Clone)  
> **Part 4** : Interface web complète avec authentification JWT, gestion des places, filtres de prix, système de reviews, et design responsive moderne.

---

## 📋 Table des matières

1. [Vue d'ensemble du projet](#-vue-densemble-du-projet)
2. [Nouveautés Part 4](#-nouveautés-part-4)
3. [Architecture globale](#-architecture-globale)
4. [Fonctionnalités](#-fonctionnalités)
5. [Pages de l'application](#-pages-de-lapplication)
6. [Technologies utilisées](#-technologies-utilisées)
7. [Arborescence](#-arborescence)
8. [Installation & Démarrage](#-installation--démarrage)
9. [Utilisation](#-utilisation)
10. [API Endpoints](#-api-endpoints)
11. [Tests](#-tests)

---

## 🌍 Vue d'ensemble du projet

HBnB Part 4 est une **application web complète** qui combine :
- ✅ **Backend API REST** sécurisée avec Flask + JWT
- ✅ **Frontend moderne** en HTML5, CSS3 et JavaScript vanilla
- ✅ **Authentification utilisateur** avec cookies JWT
- ✅ **Interface responsive** adaptée mobile/tablette/desktop
- ✅ **Design professionnel** style AirBnB avec animations

L'application permet aux utilisateurs de :
- 🔐 Se connecter avec email/password
- 🏠 Parcourir une liste de places (logements)
- 💰 Filtrer les places par prix maximum
- 📖 Voir les détails complets d'une place (prix, description, équipements, avis)
- ⭐ Laisser des avis (reviews) sur les places visitées
- 🚪 Se déconnecter proprement

---

## 🆕 Nouveautés Part 4

| # | Fonctionnalité | Description |
|---|----------------|-------------|
| 4-1 | **Page de login** | Formulaire d'authentification avec design moderne |
| 4-2 | **Page d'accueil (index)** | Liste des places en grille responsive avec filtre de prix |
| 4-3 | **Page de détails** | Affichage complet : prix, description, équipements, reviews |
| 4-4 | **Système de reviews** | Formulaire d'ajout d'avis avec note de 1 à 5 étoiles |
| 4-5 | **Authentification frontend** | Gestion des tokens JWT en cookies, affichage du prénom |
| 4-6 | **Design responsive** | Grid layout adaptatif avec media queries |
| 4-7 | **CORS** | Configuration Flask-CORS pour les requêtes cross-origin |
| 4-8 | **Script de population** | `populate_db.py` pour générer 15 places de test |

---

## 🏛️ Architecture globale

```
┌─────────────────────────────────────────────────────────────┐
│                 NAVIGATEUR WEB (Client)                     │
│   HTML5 • CSS3 • JavaScript ES6+ • Cookies JWT              │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/AJAX Fetch API
┌────────────────────────────▼────────────────────────────────┐
│              FLASK APPLICATION (Serveur)                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Static Files Server (/static/)                     │   │
│   │  • index.html  • place.html  • login.html          │   │
│   │  • scripts.js  • styles.css  • images/             │   │
│   └─────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  REST API (/api/v1/)                               │   │
│   │  • JWT Authentication  • CORS enabled               │   │
│   │  • Users  • Places  • Reviews  • Amenities         │   │
│   └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              BASE DE DONNÉES SQLite                          │
│   • users  • places  • reviews  • amenities                 │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Fonctionnalités

### 🔐 Authentification
- ✅ Formulaire de connexion avec validation
- ✅ Stockage sécurisé du token JWT en cookie
- ✅ Affichage du prénom de l'utilisateur dans le header
- ✅ Bouton de déconnexion qui supprime le cookie
- ✅ Redirection automatique si non connecté (pour reviews)

### 🏠 Gestion des Places
- ✅ Affichage en grille responsive (1 à 4 colonnes selon écran)
- ✅ Cartes avec effet hover (élévation + ombre)
- ✅ Filtre de prix dynamique (Under $50, $100, $200, All)
- ✅ Prix affiché en gros et en rouge
- ✅ Bouton "View Details" pour chaque place

### 📖 Détails d'une Place
- ✅ Titre, description, prix par nuit
- ✅ Nom complet du propriétaire
- ✅ Liste des équipements (amenities) avec badges
- ✅ Section reviews avec note en étoiles
- ✅ Formulaire d'ajout de review (si connecté)

### ⭐ Système de Reviews
- ✅ Affichage des reviews existantes avec étoiles
- ✅ Formulaire avec textarea + sélecteur de note (1-5)
- ✅ Soumission en AJAX sans rechargement de page
- ✅ Rafraîchissement automatique après ajout
- ✅ Validation : user_id, place_id, rating requis

### 🎨 Design & UX
- ✅ Header rouge style AirBnB avec logo
- ✅ Navigation propre avec hover effects
- ✅ Grille moderne avec CSS Grid
- ✅ Animations fluides (transitions 0.3s)
- ✅ Responsive : mobile (1 colonne), tablette (2-3), desktop (4)
- ✅ Ombres et arrondis pour profondeur
- ✅ Footer gris foncé

---

## 📄 Pages de l'application

### 1. **Page de Login** (`login.html`)
- URL : `http://127.0.0.1:5000/static/login.html`
- Formulaire centré avec ombre
- Validation côté client
- Redirection vers index après succès

### 2. **Page d'Accueil** (`index.html`)
- URL : `http://127.0.0.1:5000/static/index.html`
- Liste de toutes les places disponibles
- Filtre de prix dans une section blanche en haut
- Grille responsive avec gap de 24px
- Lien "View Details" sur chaque carte

### 3. **Page de Détails** (`place.html`)
- URL : `http://127.0.0.1:5000/static/place.html?id=<place_id>`
- Détails complets de la place
- Reviews avec étoiles et commentaires
- Formulaire d'ajout de review (caché si non connecté)

### 4. **Page Add Review** (`add_review.html`)
- URL : `http://127.0.0.1:5000/static/add_review.html?id=<place_id>`
- Formulaire standalone pour ajouter un review
- Redirection vers login si non authentifié

---

## 💻 Technologies utilisées

### Backend
| Package | Version | Rôle |
|---------|---------|------|
| `flask` | Latest | Framework web Python |
| `flask-restx` | Latest | Extensions REST + Swagger UI |
| `flask-sqlalchemy` | Latest | ORM pour base de données |
| `flask-bcrypt` | Latest | Hachage des mots de passe |
| `flask-jwt-extended` | Latest | Authentification JWT |
| `flask-cors` | Latest | **NOUVEAU** : Support CORS pour le frontend |

### Frontend
| Technologie | Usage |
|-------------|-------|
| **HTML5** | Structure sémantique des pages |
| **CSS3** | Design moderne avec Grid, Flexbox, animations |
| **JavaScript ES6+** | Logique client, AJAX avec Fetch API |
| **Cookies** | Stockage du JWT pour persistance de session |

### Base de données
- **SQLite** : `instance/development.db`
- **Tables** : users, places, reviews, amenities, place_amenity

---

## 🗂️ Arborescence

```
part4/
│
├── run.py                          ← Point d'entrée du serveur
├── config.py                       ← Configuration (legacy)
├── requirements.txt                ← Dépendances Python (+ flask-cors)
├── populate_db.py                  ← Script pour peupler la DB avec 15 places
├── ER_diagram.md                   ← Diagramme ER de la base
│
├── instance/
│   └── development.db              ← Base SQLite (créée au démarrage)
│
├── static/                         ← **NOUVEAU : Fichiers frontend**
│   ├── index.html                  ← Page d'accueil (liste places)
│   ├── login.html                  ← Page de connexion
│   ├── place.html                  ← Page de détails d'une place
│   ├── add_review.html             ← Page d'ajout de review
│   ├── scripts.js                  ← Logique JavaScript (710 lignes)
│   ├── styles.css                  ← Styles CSS (400 lignes)
│   └── images/
│       ├── logo.png                ← Logo HBnB
│       └── icon.png                ← Favicon
│
└── app/
    ├── __init__.py                 ← Factory Flask + CORS + Static files
    ├── config.py                   ← Dev/Test/Prod configs
    │
    ├── api/
    │   └── v1/
    │       ├── users.py            ← Endpoints users + login
    │       ├── places.py           ← **MODIFIÉ** : Ajout champ price
    │       ├── reviews.py          ← Endpoints reviews
    │       └── amenities.py        ← Endpoints amenities
    │
    ├── models/
    │   ├── base_model.py           ← BaseModel SQLAlchemy
    │   ├── user.py                 ← User avec bcrypt
    │   ├── place.py                ← Place avec relations
    │   ├── amenity.py              ← Amenity
    │   └── review.py               ← Review avec validation
    │
    ├── persistence/
    │   └── repository.py           ← Repository pattern
    │
    ├── services/
    │   └── facade.py               ← HBnBFacade (business logic)
    │
    └── tests/
        └── test_part3_full.py      ← 50 tests automatisés
```

---

## 🚀 Installation & Démarrage

### Prérequis
- Python 3.8+
- pip

### Installation

```bash
# 1. Naviguer dans le dossier part4
cd part4

# 2. Créer l'environnement virtuel
python -m venv venve

# 3. Activer l'environnement
venve\Scripts\activate      # Windows
source venve/bin/activate   # Linux/Mac

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer le serveur Flask
python run.py
```

Le serveur démarre sur **http://127.0.0.1:5000**

### Peupler la base de données

```bash
# Dans un autre terminal (avec venve activé)
python populate_db.py
```

Cela crée automatiquement :
- ✅ 1 utilisateur admin : **marie.dubois@example.com** (password: `marie123`)
- ✅ 8 équipements (WiFi, Parking, Pool, Kitchen, AC, TV, Gym, Pet Friendly)
- ✅ 15 places variées de 45€ à 650€/nuit

---

## 🎯 Utilisation

### 1. Accéder à l'application

Ouvrez votre navigateur et allez sur :
```
http://127.0.0.1:5000/static/index.html
```

### 2. Se connecter

- Cliquez sur **Login** dans le header
- Utilisez les identifiants :
  - **Email** : `marie.dubois@example.com`
  - **Password** : `marie123`
- Vous serez redirigé vers la liste des places

### 3. Explorer les places

- Utilisez le **filtre de prix** en haut pour afficher seulement les places :
  - Under $50
  - Under $100
  - Under $200
  - All (toutes)
- Cliquez sur **View Details** pour voir une place

### 4. Ajouter un review

- Sur la page de détails, scrollez jusqu'à "Add a Review"
- Écrivez votre commentaire
- Sélectionnez une note (1 à 5 étoiles)
- Cliquez sur **Submit Review**
- Les reviews se rafraîchissent automatiquement

### 5. Se déconnecter

- Cliquez sur **Logout** dans le header
- Vous serez redirigé vers la page de login

---

## 🔌 API Endpoints

### Documentation Swagger
```
http://127.0.0.1:5000/doc
```

### Endpoints principaux utilisés par le frontend

| Méthode | Endpoint | Usage Frontend |
|---------|----------|----------------|
| `POST /api/v1/users/login` | Authentification utilisateur |
| `GET /api/v1/users/me` | Récupérer le prénom de l'utilisateur connecté |
| `GET /api/v1/places/` | Charger la liste des places (index.html) |
| `GET /api/v1/places/<id>` | Charger les détails d'une place (place.html) |
| `GET /api/v1/reviews/places/<id>/reviews` | Charger les reviews d'une place |
| `POST /api/v1/reviews/` | Soumettre un nouveau review |

### Authentification JWT

Le frontend stocke le token JWT dans un **cookie** nommé `token` :
```javascript
document.cookie = `token=${access_token}; path=/`;
```

Toutes les requêtes protégées incluent le header :
```javascript
headers: { 'Authorization': `Bearer ${token}` }
```

---

## 🧪 Tests

### Tests backend (50 tests)

```bash
cd part4
python -m pytest app/tests/test_part3_full.py -v
```

Résultat attendu : **50 passed**

### Tests manuels frontend

| Test | Procédure | Résultat attendu |
|------|-----------|------------------|
| **Login** | Entrer email/password valides | Redirection vers index, prénom affiché |
| **Login invalide** | Entrer mauvais password | Alert "Login failed" |
| **Liste places** | Ouvrir index.html | 15 places affichées en grille |
| **Filtre prix** | Sélectionner "Under $100" | Seulement places ≤ 100€ affichées |
| **Détails place** | Cliquer "View Details" | Page détails avec équipements et reviews |
| **Add review (connecté)** | Remplir formulaire + Submit | Alert "success", reviews rafraîchies |
| **Add review (déconnecté)** | Ouvrir place.html sans login | Formulaire caché, "Login" affiché |
| **Logout** | Cliquer Logout | Redirection login, cookie supprimé |
| **Responsive** | Réduire fenêtre | Layout adapte : 4 → 3 → 2 → 1 colonne |

---

## 🎨 Design Features

### Color Palette
- **Primary** : `#ff5a5f` (rouge AirBnB)
- **Background** : `#f5f5f5` (gris clair)
- **Cards** : `#ffffff` (blanc)
- **Text** : `#333` (gris foncé)
- **Footer** : `#333` (gris foncé)

### Responsive Breakpoints
```css
@media (max-width: 1200px) { /* 3 colonnes */ }
@media (max-width: 768px)  { /* 2 colonnes */ }
@media (max-width: 480px)  { /* 1 colonne */ }
```

### Animations
- **Hover cards** : `transform: translateY(-4px)` + shadow
- **Buttons** : `transform: translateY(-2px)` + shadow
- **Transitions** : `0.3s ease` sur tous les effets

---

## 📊 Structure du code JavaScript

### Fichier `scripts.js` (710 lignes)

```javascript
// ── Configuration ──
const API_URL = 'http://127.0.0.1:5000';

// ── Event Listeners (DOMContentLoaded) ──
// • Login form submit
// • Price filter change
// • Place details page load
// • Add review form submit

// ── Helpers ──
getCookie(name)              // Récupère un cookie
getPlaceIdFromURL()          // Parse l'ID depuis ?id=...
getTokenPayload(token)       // Décode le JWT

// ── Authentication ──
checkAuthentication()        // Index : show/hide login, fetch places
checkAuthenticationPlace()   // Place : show/hide review form
checkAuthenticationReview()  // Add review : redirect si non connecté
fetchCurrentUser(token)      // GET /users/me → affiche prénom

// ── Login ──
loginUser(email, password)   // POST /users/login → cookie + redirect

// ── Places ──
fetchPlaces(token)           // GET /places/ → displayPlaces()
displayPlaces(places)        // Crée les cards avec dataset.price

// ── Place Details ──
fetchPlaceDetails(token, id) // GET /places/<id> → displayPlaceDetails()
displayPlaceDetails(place)   // Affiche owner, amenities, etc.

// ── Reviews ──
fetchReviews(token, placeId) // GET /reviews/places/<id>/reviews
displayReviews(reviews)      // Affiche étoiles + commentaires

// ── Add Review ──
submitReview(token, placeId, comment, rating) // POST /reviews/
handleResponse(response)     // Alert + refresh reviews
```

---

## 🐛 Corrections apportées (par rapport aux PRs)

| # | Problème | Correction | Fichier |
|---|----------|-----------|---------|
| 1 | CORS manquant | Ajout `flask-cors` + `CORS(app)` | `app/__init__.py` |
| 2 | Champ `price` manquant dans liste places | Ajout `'price': place.price` | `api/v1/places.py` |
| 3 | ID textarea incohérent | `id="review-text"` → `id="review"` | `place.html` |
| 4 | Pas de logout | Ajout bouton + fonction `logout` | `scripts.js` |
| 5 | Layout en colonnes | CSS Grid responsive | `styles.css` |
| 6 | Pas de nom utilisateur | Ajout `fetchCurrentUser()` + affichage | `scripts.js` |

---

## 📝 Crédits

- **Projet** : Holberton School — HBnB (AirBnB Clone)
- **Part 4** : Frontend Web Application
- **Auteur** : Marie Dubois (example)
- **Technologies** : Flask, SQLAlchemy, JWT, HTML5, CSS3, JavaScript ES6+

---

## 📞 Support

**API Documentation** : http://127.0.0.1:5000/doc  
**Frontend** : http://127.0.0.1:5000/static/index.html

Pour toute question, consultez la documentation Swagger ou les tests automatisés.

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
