# Documentation de l'API : Création d'Utilisateur

Ce document décrit le flux logique et technique de l'endpoint d'inscription des utilisateurs.

## 📌 Aperçu du Flux
L'architecture repose sur un modèle en couches (API > Facade > Model > Repository) pour assurer une séparation nette des responsabilités et une validation robuste.



---

## 🚀 Spécifications de l'Endpoint

**Requête :** `POST /users`

### Corps de la requête (JSON)
| Champ | Type | Description |
| :--- | :--- | :--- |
| `email` | String | Email unique de l'utilisateur (Requis) |
| `password` | String | Minimum 8 caractères (Requis) |
| `first_name`| String | Prénom de l'utilisateur |
| `last_name` | String | Nom de l'utilisateur |

---

## 🛠 Gestion des Réponses

### 🟢 Succès
* **201 Created** : Utilisateur créé avec succès. Retourne l'objet avec `id` et `created_at`.

### 🟠 Erreurs Client (4xx)
* **400 Bad Request** : 
    * Champs requis manquants.
    * Format d'email invalide.
    * Mot de passe trop faible.
* **409 Conflict** : Email déjà utilisé dans la base de données.

### 🔴 Erreurs Serveur (5xx)
* **500 Internal Server Error** : Échec de connexion à la base de données.
* **504 Gateway Timeout** : Délai d'attente de la base de données dépassé.

---

## 🏗 Composants Techniques
1.  **API (Controller)** : Point d'entrée, gère les protocoles HTTP.
2.  **Facade** : Orchestrateur entre la logique métier et les modèles.
3.  **UserModel** : Responsable de la structure et des règles de validation.
4.  **Repository** : Interface d'abstraction pour les requêtes SQL/NoSQL.
5.  **Database** : Persistance physique des données.