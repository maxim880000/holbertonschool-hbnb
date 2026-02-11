# Architecture 3 Couches - Projet HBnB

Ce document explique l'architecture en **3 couches** utilisée dans le projet HBnB.  
Chaque couche a **une responsabilité unique**, ce qui rend le projet propre, modulable et facile à maintenir.

---

## 1️⃣ Presentation Layer

**Rôle principal :** gérer l’interaction avec l’utilisateur ou d’autres applications.  

**Composants :**
- **API** : permet à l’application front (site web, appli mobile) de communiquer avec le back-end.
- **Endpoints** : URL de l’API correspondant à une action (ex : `/users`, `/places`, `/reviews`).
- **Controllers** : fonctions qui s’exécutent lorsque l’endpoint est appelé.

**Fonctionnement :**
1. Le client envoie une requête (ex : `POST /users` pour créer un utilisateur).
2. L’API reçoit la requête.
3. L’endpoint correspondant est identifié.
4. Le controller lié à cet endpoint s’exécute.
5. Le controller récupère et valide les données.
6. Le controller appelle la **Facade** (Business Logic Layer) pour traiter la requête.
7. La réponse finale est renvoyée au client.

**Notes importantes :**
- Endpoint = URL de l’API.
- API = système qui reçoit et répond.
- Controller = fonction qui gère l’endpoint.

**Dans HBnB, exemples d’utilisation :**
- Créer un utilisateur → `POST /users`
- Voir tous les logements → `GET /places`
- Poster un avis → `POST /reviews`

**Règles simples pour les méthodes HTTP :**
- `GET` = récupérer des informations  
- `POST` = créer quelque chose  
- `PUT / PATCH` = modifier  
- `DELETE` = supprimer  

---

## 2️⃣ Business Logic Layer

**Rôle principal :** gérer toute la logique métier du projet.  

**Composants :**
- **Facade Interface** : coordonne toutes les demandes venant de l’API et décide quoi faire. C’est le chef d’orchestre de la couche métier.
- **Business Models** : représentent les entités importantes du projet (`User`, `Place`, `Review`, `Amenity`) et contiennent les règles associées.

**Responsabilités :**
- Vérifier que toutes les actions respectent les règles métier.
- Centraliser la logique pour que le controller ne fasse que transmettre les demandes.
- Interagir avec la couche de persistance via les repositories pour stocker ou récupérer les données.

**Résumé :**
- Facade = reçoit et dirige les demandes  
- Business Models = contiennent les données et les règles des entités du projet  

---

## 3️⃣ Persistence Layer

**Rôle principal :** gérer le stockage et la récupération des données.  

**Composants :**
- **Repositories / DAO** : intermédiaires entre les modèles et la base de données.  
  - Sauvegardent, récupèrent, mettent à jour et suppriment les données.  
  - Cachent les détails du stockage pour que la couche métier ne s’en occupe pas.  
- **Database (JSON / MySQL)** : stockage réel des données.

**Responsabilité :**
- Assurer que toutes les données sont persistées correctement.  
- Garantir l’indépendance entre la logique métier et la méthode de stockage.  

---

## Résumé global

| Couche | Rôle principal | Exemples de composants |
|--------|----------------|----------------------|
| Presentation Layer | Interaction avec l’utilisateur / API | Endpoints, Controllers |
| Business Logic Layer | Logique métier / règles | Facade, Models (User, Place, Review, Amenity) |
| Persistence Layer | Stockage des données | Repositories / DAO, Database |

**Flux général :**  
`Client → Presentation Layer → Business Logic Layer → Persistence Layer → Database`

Chaque couche a **une seule responsabilité**, ce qui rend le projet **modulaire et maintenable**.

---

## Diagramme Mermaid de l’architecture

```mermaid
flowchart TD
    %% Couche de Présentation
    subgraph "Presentation Layer"
        A["API Services<br/>Endpoints<br/>Controllers<br/>- Reçoit les requêtes<br/>- Trouve l'endpoint<br/>- Appelle la Facade"]
    end

    %% Couche Logique Métier
    subgraph "Business Logic Layer"
        F["Facade Interface<br/>- Coordonne les demandes de l'API<br/>- Décide quoi faire"]
        B["Business Models<br/>User, Place, Review, Amenity<br/>- Contiennent les données et règles du projet"]
    end

    %% Couche Persistance
    subgraph "Persistence Layer"
        C["Repositories / DAO<br/>- Sauvegarde et récupère les données<br/>- Intermédiaire entre Models et Database"]
        D[("Database<br/>JSON / MySQL<br/>- Stocke les données réelles")]
    end

    %% Connexions
    A --> F
    F --> B
    B --> C
    C --> D

    %% Styles
    classDef layer fill:#ffffff,stroke:#000,stroke-width:2px,color:#000
    classDef facade fill:#f0f0f0,stroke:#333,stroke-width:2px,color:#000
    class A,B,C,D layer
    class F facade
