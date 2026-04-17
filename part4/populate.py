"""
populate.py — Seed the HBnB database with test data.

Usage:
    python populate.py

The Flask server must already be running on http://127.0.0.1:5001.
"""

import requests

BASE = "http://127.0.0.1:5001/api/v1"


def post(path, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(f"{BASE}{path}", json=data, headers=headers)
    if r.status_code not in (200, 201):
        print(f"  ERROR {r.status_code} on POST {path}: {r.text}")
        return None
    return r.json()


def get(path):
    r = requests.get(f"{BASE}{path}")
    if r.status_code == 200:
        return r.json()
    return None


def main():
    print("=== Seeding HBnB database ===\n")

    print("[1/5] Creating admin user...")
    admin = post("/users/", {
        "email": "admin@hbnb.io",
        "password": "Admin1234!",
        "first_name": "Admin",
        "last_name": "HBnB",
    })
    if not admin:
        print("      Admin may already exist. Trying login only.")

    print("[2/5] Logging in as admin...")
    login = post("/users/login", {
        "email": "admin@hbnb.io",
        "password": "Admin1234!",
    })
    if not login:
        print("      Could not log in. Aborting.")
        return
    token = login["access_token"]
    print("      Token obtained.\n")

    print("[3/5] Creating regular users...")
    users_data = [
        {"email": "alice@hbnb.io",   "password": "Password1!", "first_name": "Alice",   "last_name": "Dupont"},
        {"email": "bob@hbnb.io",     "password": "Password1!", "first_name": "Bob",     "last_name": "Martin"},
        {"email": "charlie@hbnb.io", "password": "Password1!", "first_name": "Charlie", "last_name": "Bernard"},
    ]
    users = {}
    all_users = get("/users/") or []
    for ud in users_data:
        existing = next((u for u in all_users if u["email"] == ud["email"]), None)
        if existing:
            users[ud["email"]] = existing
            print(f"      Found existing user {ud['email']} — id={existing['id']}")
        else:
            u = post("/users/", ud, token=token)
            if u:
                users[ud["email"]] = u
                print(f"      Created user {ud['email']} — id={u['id']}")

    print("\n[4/5] Creating amenities...")
    amenity_names = ["WiFi", "Pool", "Parking", "Air conditioning", "Kitchen", "Pet-friendly"]
    amenities = {}
    for name in amenity_names:
        a = post("/amenities/", {"name": name}, token=token)
        if a:
            amenities[name] = a
            print(f"      Created amenity '{name}' — id={a['id']}")

    print("\n[5/5] Creating places and reviews...")

    alice_id   = users.get("alice@hbnb.io",   {}).get("id")
    bob_id     = users.get("bob@hbnb.io",     {}).get("id")
    charlie_id = users.get("charlie@hbnb.io", {}).get("id")

    places_data = [
        {
            "title": "Cozy Studio in Paris",
            "description": "A charming studio in the heart of Paris, close to all attractions.",
            "price": 75.0, "latitude": 48.8566, "longitude": 2.3522,
            "owner_id": alice_id, "amenities": [], "max_guests": 2,
        },
        {
            "title": "Seaside Villa",
            "description": "Stunning villa with private pool and direct beach access.",
            "price": 250.0, "latitude": 43.2965, "longitude": 5.3818,
            "owner_id": bob_id, "amenities": [], "max_guests": 8,
        },
        {
            "title": "Mountain Chalet",
            "description": "Rustic chalet perfect for ski lovers, pet-friendly.",
            "price": 120.0, "latitude": 45.9237, "longitude": 6.8694,
            "owner_id": charlie_id, "amenities": [], "max_guests": 6,
        },
        {
            "title": "Budget Room Lyon",
            "description": "Affordable private room near Lyon city center.",
            "price": 30.0, "latitude": 45.7640, "longitude": 4.8357,
            "owner_id": alice_id, "amenities": [], "max_guests": 1,
        },
    ]

    def get_token(email, password):
        r = post("/users/login", {"email": email, "password": password})
        return r["access_token"] if r else None

    alice_token   = get_token("alice@hbnb.io",   "Password1!")
    bob_token     = get_token("bob@hbnb.io",     "Password1!")
    charlie_token = get_token("charlie@hbnb.io", "Password1!")

    place_ids = []
    for pd in places_data:
        p = post("/places/", pd, token=token)
        if p:
            place_ids.append((p["id"], pd["owner_id"]))
            print(f"      Created place '{pd['title']}' — id={p['id']}")

    user_ids = {
        alice_token:   alice_id,
        bob_token:     bob_id,
        charlie_token: charlie_id,
    }

    reviews_data = [
        {"token": bob_token,     "place_idx": 0, "rating": 5, "comment": "Absolutely loved it! Very cozy and central."},
        {"token": charlie_token, "place_idx": 0, "rating": 4, "comment": "Great location, a bit small but very clean."},
        {"token": alice_token,   "place_idx": 1, "rating": 5, "comment": "Dream villa, the pool is amazing!"},
        {"token": charlie_token, "place_idx": 1, "rating": 4, "comment": "Excellent stay, would come back."},
        {"token": alice_token,   "place_idx": 2, "rating": 4, "comment": "Perfect chalet, my dog loved it too."},
        {"token": bob_token,     "place_idx": 2, "rating": 3, "comment": "Nice place but a bit cold at night."},
        {"token": bob_token,     "place_idx": 3, "rating": 4, "comment": "Great value for money, very clean room."},
    ]

    for rd in reviews_data:
        if rd["place_idx"] >= len(place_ids):
            continue
        place_id, _ = place_ids[rd["place_idx"]]
        uid = user_ids.get(rd["token"])
        if not uid or not rd["token"]:
            continue
        review = post("/reviews/", {
            "place_id": place_id,
            "user_id":  uid,
            "rating":   rd["rating"],
            "comment":  rd["comment"],
        }, token=rd["token"])
        if review:
            print(f"      Review added for place {place_id} by user {uid}")

    print("\n=== Done! Database seeded successfully. ===")
    print("Admin credentials : admin@hbnb.io / Admin1234!")
    print("User credentials  : alice@hbnb.io, bob@hbnb.io, charlie@hbnb.io / Password1!")


if __name__ == "__main__":
    main()
