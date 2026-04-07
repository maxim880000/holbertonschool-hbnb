# HBnB — Entity-Relationship Diagram

This diagram represents the database schema for the HBnB project.
It was generated using [Mermaid.js](https://mermaid.js.org/) and reflects the SQLAlchemy models defined in `app/models/`.

---

```mermaid
erDiagram

    USER {
        string id PK
        string first_name
        string last_name
        string email
        string password
        boolean is_admin
        datetime created_at
        datetime updated_at
    }

    PLACE {
        string id PK
        string title
        string description
        float price
        float latitude
        float longitude
        int max_guests
        boolean is_available
        string owner_id FK
        datetime created_at
        datetime updated_at
    }

    REVIEW {
        string id PK
        string text
        int rating
        string user_id FK
        string place_id FK
        datetime created_at
        datetime updated_at
    }

    AMENITY {
        string id PK
        string name
        string description
        datetime created_at
        datetime updated_at
    }

    PLACE_AMENITY {
        string place_id FK
        string amenity_id FK
    }

    USER ||--o{ PLACE : "owns"
    USER ||--o{ REVIEW : "writes"
    PLACE ||--o{ REVIEW : "has"
    PLACE ||--o{ PLACE_AMENITY : "links"
    AMENITY ||--o{ PLACE_AMENITY : "linked by"
```

---

## Relationships

| Relationship | Type | Description |
|---|---|---|
| USER → PLACE | One-to-Many | A user can own multiple places |
| USER → REVIEW | One-to-Many | A user can write multiple reviews |
| PLACE → REVIEW | One-to-Many | A place can have multiple reviews |
| PLACE ↔ AMENITY | Many-to-Many | A place can have multiple amenities, an amenity can belong to multiple places (via `PLACE_AMENITY`) |
