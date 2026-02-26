# Documentation de l'API : Recherche de Lieux (Places)

Ce document détaille le fonctionnement de l'endpoint permettant de filtrer et de récupérer des lieux en fonction de critères spécifiques.

## 📌 Flux de Recherche
Le système utilise une architecture découplée où la **Facade** centralise la logique de filtrage avant de solliciter le **Repository**.



---

## 🚀 Spécifications de l'Endpoint

**Requête :** `GET /places`

### Paramètres de Requête (Query Params) 
| Paramètre | Type | Description |
| :--- | :--- | :--- |
| `location` | String | Ville ou région cible (ex: Paris) |
| `max_price`| Number | Prix maximum autorisé |

---

## 🛠 Gestion des Réponses

### 🟢 Succès
* **200 OK (Données)** : Retourne une liste d'objets `place` correspondant aux critères.
* **200 OK (Vide)** : Retourne un tableau vide `[]` si aucun lieu ne correspond, sans erreur serveur.

### 🟠 Erreurs Client (4xx)
* **400 Bad Request** : Paramètres de requête invalides ou mal formatés.

### 🔴 Erreurs Serveur (5xx)
* **500 Internal Server Error** : Échec critique de communication avec la base de données.

---

## 🏗 Logique Interne
1.  **Validation** : L'API vérifie la validité des paramètres `location` et `max_price`.
2.  **Abstraction** : Le `Repository` traduit les filtres en requêtes SQL complexes (`LIKE`, `<=`).
3.  **Formatage** : La `Facade` formate les objets bruts de la base de données avant de les renvoyer à l'API.