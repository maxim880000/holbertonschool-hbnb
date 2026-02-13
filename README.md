# Holberton AirBnB — Projet HBNB

Un clone pédagogique simplifié d'AirBnB (projet Holberton). Ce dépôt contient l'implémentation des modèles, du stockage et d'une console interactive (REPL) pour créer, lire, mettre à jour et supprimer des objets.

---

## 🚀 Aperçu

- Objectif : reproduire les fonctionnalités de base d'AirBnB pour apprendre la conception orientée objet, la sérialisation et les tests.
- Fonctions principales : console interactive, modèles (User, Place, State, City, Amenity, Review), stockage (fichier JSON / DB), tests unitaires.

---

## ⚙️ Prérequis

- Python 3.8+ (cet espace de travail contient `hbnb_venv` avec Python 3.14).
- virtualenv (optionnel si vous utilisez `hbnb_venv` fourni).

---

## 📥 Installation rapide

1. Activer l'environnement virtuel fourni :

   ```bash
   source hbnb_venv/bin/activate
   ```

2. (Optionnel) Installer les dépendances si un `requirements.txt` est présent :

   ```bash
   pip install -r requirements.txt
   ```

3. Lancer la console (si le fichier `console.py` est présent) :

   ```bash
   python console.py
   ```

---

## ▶️ Utilisation (exemples de commandes `console`)

- `create <ClassName>` — crée une instance et affiche son id
- `show <ClassName> <id>` — affiche l'objet
- `destroy <ClassName> <id>` — supprime l'objet
- `all [<ClassName>]` — liste toutes les instances (ou celles d'une classe)
- `update <ClassName> <id> <attribute_name> "<value>"` — met à jour un attribut

Exemple :

```bash
$ create User
$ show User 1234-1234-1234
$ update User 1234-1234-1234 email "user@example.com"
$ all User
```

---

## ✅ Tests & style

- Tests unitaires (si fournis) :

  ```bash
  python -m unittest discover -v
  ```

- Vérification du style (PEP8) :

  ```bash
  pycodestyle .
  ```

---

## 📁 Structure attendue

- `console.py` — interface en ligne de commande (REPL)
- `models/` — classes de données et logique métier
- `tests/` — tests unitaires
- `hbnb_venv/` — environnement virtuel local (fourni)
- `README.md` — documentation (ce fichier)

(Remarque : l'arborescence exacte peut varier selon votre version du projet.)

---

## 🤝 Contribution

- Ouvrez une issue pour signaler un bug ou proposer une amélioration.
- Soumettez une pull request avec des tests associés.

---

## 🧾 Auteur

- Hugo Ramos — [GitHub](https://github.com/hugou74130)
- Maxim Dutruel — [GitHub](https://github.com/maxim880000)
- Carlos Silva — [GitHub](https://github.com/CodexSC's)
---

