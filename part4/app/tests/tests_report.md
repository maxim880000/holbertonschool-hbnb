# HBnB API – Testing Report

## Summary

| Suite | Tests | Passed | Failed |
| --- | --- | --- | --- |
| `test_api.py` (Users CRUD) | 2 | 2 | 0 |
| `test_models.py` (Unit – validation) | 43 | 43 | 0 |
| `test_endpoint.py` (Integration – all endpoints) | 36 | 36 | 0 |
| **Total** | **81** | **81** | **0** |

Run command: `python -m unittest discover -s app/tests -v`

---

## Validation Implemented

### User Validation

| Rule | Implementation |
| --- | --- |
| `first_name` not empty, max 50 chars | `User.__init__` raises `ValueError` |
| `last_name` not empty, max 50 chars | `User.__init__` raises `ValueError` |
| `email` valid format (`local@domain.tld`) | regex `^[^@\s]+@[^@\s]+\.[^@\s]+$` |
| `password` not empty | `User.__init__` raises `ValueError` |
| Email unique | `HBnBFacade.create_user` checks repo, raises `ValueError` → HTTP 409 |
| Password never exposed | `to_dict()` omits `password_hash` |

### Place Validation

| Rule | Implementation |
| --- | --- |
| `title` not empty, max 100 chars | `Place.__init__` raises `ValueError` |
| `price` strictly positive (> 0) | `Place.__init__` raises `ValueError` |
| `latitude` in `[-90, 90]` | `Place.__init__` raises `ValueError` |
| `longitude` in `[-180, 180]` | `Place.__init__` raises `ValueError` |
| `owner_id` must reference existing User | `HBnBFacade.create_place` raises `ValueError` |
| Amenity IDs must reference existing Amenities | `HBnBFacade.create_place` raises `ValueError` |

### Review Validation

| Rule | Implementation |
| --- | --- |
| `comment` not empty | `Review.__init__` raises `ValueError` |
| `rating` integer in `[1, 5]` | `Review.__init__` raises `ValueError` |
| `user_id` must reference existing User | `HBnBFacade.create_review` raises `ValueError` → HTTP 404 |
| `place_id` must reference existing Place | `HBnBFacade.create_review` raises `ValueError` → HTTP 404 |

### Amenity Validation

| Rule | Implementation |
| --- | --- |
| `name` not empty, max 50 chars | `Amenity.__init__` raises `ValueError` |

---

## Test Cases – `test_models.py` (Unit Tests)

### User Model Tests

| Test | Input | Expected | Result |
| --- | --- | --- | --- |
| `test_valid_user_creation` | Valid data | Object created with correct fields | PASS |
| `test_password_is_hashed` | Password `mypassword` | Stored hash ≠ plaintext; `authenticate()` works | PASS |
| `test_to_dict_excludes_password` | Any user | Dict has no `password` or `password_hash` key | PASS |
| `test_missing_first_name` | `first_name=''` | `ValueError` | PASS |
| `test_missing_last_name` | `last_name=''` | `ValueError` | PASS |
| `test_missing_email` | `email=''` | `ValueError` | PASS |
| `test_invalid_email_no_at` | `invalidemail.com` | `ValueError` | PASS |
| `test_invalid_email_no_domain` | `user@` | `ValueError` | PASS |
| `test_invalid_email_no_tld` | `user@domain` | `ValueError` | PASS |
| `test_missing_password` | `password=''` | `ValueError` | PASS |
| `test_first_name_too_long` | 51-char string | `ValueError` | PASS |
| `test_last_name_too_long` | 51-char string | `ValueError` | PASS |
| `test_is_admin_flag` | `is_admin=True` | Flag stored correctly | PASS |

### Place Model Tests

| Test | Input | Expected | Result |
| --- | --- | --- | --- |
| `test_valid_place_creation` | Valid data | Object created; empty `reviews`/`amenities` | PASS |
| `test_empty_title` | `title=''` | `ValueError` | PASS |
| `test_title_too_long` | 101-char title | `ValueError` | PASS |
| `test_zero_price` | `price=0` | `ValueError` | PASS |
| `test_negative_price` | `price=-10` | `ValueError` | PASS |
| `test_latitude_too_high` | `latitude=91` | `ValueError` | PASS |
| `test_latitude_too_low` | `latitude=-91` | `ValueError` | PASS |
| `test_latitude_boundary_valid` | `latitude=±90` | No error | PASS |
| `test_longitude_too_high` | `longitude=181` | `ValueError` | PASS |
| `test_longitude_too_low` | `longitude=-181` | `ValueError` | PASS |
| `test_longitude_boundary_valid` | `longitude=±180` | No error | PASS |
| `test_owner_required` | `owner=None` | `ValueError` | PASS |
| `test_add_amenity` | Add same amenity twice | Stored once | PASS |
| `test_average_rating_no_reviews` | No reviews | Returns `0.0` | PASS |
| `test_to_dict_contains_owner_id` | Any place | Dict has `owner_id`, no `owner` object | PASS |

### Review Model Tests

| Test | Input | Expected | Result |
| --- | --- | --- | --- |
| `test_valid_review` | Valid data | Object created | PASS |
| `test_empty_comment` | `comment=''` | `ValueError` | PASS |
| `test_rating_zero` | `rating=0` | `ValueError` | PASS |
| `test_rating_six` | `rating=6` | `ValueError` | PASS |
| `test_rating_float` | `rating=3.5` | `ValueError` | PASS |
| `test_rating_boundary_1` | `rating=1` | No error | PASS |
| `test_rating_boundary_5` | `rating=5` | No error | PASS |
| `test_missing_place` | `place=None` | `ValueError` | PASS |
| `test_missing_user` | `user=None` | `ValueError` | PASS |
| `test_to_dict_uses_ids` | Any review | Dict has `place_id`/`user_id`, not objects | PASS |

### Amenity Model Tests

| Test | Input | Expected | Result |
| --- | --- | --- | --- |
| `test_valid_amenity` | `name='Pool'` | Object created; empty description | PASS |
| `test_amenity_with_description` | `description='...'` | Stored correctly | PASS |
| `test_empty_name` | `name=''` | `ValueError` | PASS |
| `test_name_too_long` | 51-char name | `ValueError` | PASS |
| `test_to_dict` | Any amenity | Dict has `id` and `name` | PASS |

---

## Test Cases – `test_endpoint.py` (Integration Tests)

### Amenity Endpoints (`/api/v1/amenities/`)

| Test | Method + Path | Input | Expected Status | Result |
| --- | --- | --- | --- | --- |
| `test_create_amenity_success` | POST `/amenities/` | `name=Pool` | 201 + id in body | PASS |
| `test_create_amenity_empty_name` | POST `/amenities/` | `name=''` | 400 | PASS |
| `test_create_amenity_name_too_long` | POST `/amenities/` | 51-char name | 400 | PASS |
| `test_list_amenities` | GET `/amenities/` | — | 200 + list | PASS |
| `test_get_amenity_by_id` | GET `/amenities/{id}` | Valid id | 200 | PASS |
| `test_get_amenity_not_found` | GET `/amenities/nonexistent` | — | 404 | PASS |
| `test_update_amenity` | PUT `/amenities/{id}` | `name=Rooftop Garden` | 200 + updated name | PASS |
| `test_update_amenity_not_found` | PUT `/amenities/nonexistent` | — | 404 | PASS |

### Place Endpoints (`/api/v1/places/`)

| Test | Method + Path | Input | Expected Status | Result |
| --- | --- | --- | --- | --- |
| `test_create_place_success` | POST `/places/` | Valid data + valid owner | 201 + owner_id | PASS |
| `test_create_place_with_amenity` | POST `/places/` | Valid data + amenity id | 201 | PASS |
| `test_create_place_invalid_owner` | POST `/places/` | `owner_id=bad-owner-id` | 400 | PASS |
| `test_create_place_empty_title` | POST `/places/` | `title=''` | 400 | PASS |
| `test_create_place_zero_price` | POST `/places/` | `price=0` | 400 | PASS |
| `test_create_place_negative_price` | POST `/places/` | `price=-5` | 400 | PASS |
| `test_create_place_latitude_out_of_range` | POST `/places/` | `latitude=95` | 400 | PASS |
| `test_create_place_longitude_out_of_range` | POST `/places/` | `longitude=200` | 400 | PASS |
| `test_list_places` | GET `/places/` | — | 200 + non-empty list | PASS |
| `test_get_place_by_id` | GET `/places/{id}` | Valid id | 200 + owner + amenities | PASS |
| `test_get_place_not_found` | GET `/places/nonexistent` | — | 404 | PASS |
| `test_update_place` | PUT `/places/{id}` | Valid updated fields | 200 | PASS |
| `test_update_place_not_found` | PUT `/places/nonexistent` | — | 404 | PASS |

### Review Endpoints (`/api/v1/reviews/`)

| Test | Method + Path | Input | Expected Status | Result |
| --- | --- | --- | --- | --- |
| `test_create_review_success` | POST `/reviews/` | `rating=4, comment=Nice!` | 201 | PASS |
| `test_create_review_invalid_user` | POST `/reviews/` | `user_id=bad-user` | 404 | PASS |
| `test_create_review_invalid_place` | POST `/reviews/` | `place_id=bad-place` | 404 | PASS |
| `test_create_review_empty_comment` | POST `/reviews/` | `comment=''` | 400 | PASS |
| `test_create_review_rating_too_low` | POST `/reviews/` | `rating=0` | 400 | PASS |
| `test_create_review_rating_too_high` | POST `/reviews/` | `rating=6` | 400 | PASS |
| `test_list_reviews` | GET `/reviews/` | — | 200 + list | PASS |
| `test_get_review_by_id` | GET `/reviews/{id}` | Valid id | 200 | PASS |
| `test_get_review_not_found` | GET `/reviews/nonexistent` | — | 404 | PASS |
| `test_update_review` | PUT `/reviews/{id}` | `rating=5, comment=Even better!` | 200 | PASS |
| `test_update_review_not_found` | PUT `/reviews/nonexistent` | — | 404 | PASS |
| `test_delete_review` | DELETE `/reviews/{id}` | Valid id | 200; GET returns 404 | PASS |
| `test_delete_review_not_found` | DELETE `/reviews/nonexistent` | — | 404 | PASS |
| `test_get_reviews_by_place` | GET `/reviews/places/{id}/reviews` | Valid place with 2 reviews | 200 + list of 2 | PASS |
| `test_get_reviews_by_invalid_place` | GET `/reviews/places/bad-place/reviews` | — | 404 | PASS |

---

## Bugs Found and Fixed

| Bug | Fix |
| --- | --- |
| `users.py` instantiated its own `HBnBFacade()` instead of using the shared singleton, so users created via `/users/` were invisible to `/places/` | Changed import to `from app.services import facade` |
| `test_duplicate_email` sent only `email`+`password`, but `User.__init__` requires `first_name`+`last_name` positionally | Added `first_name`/`last_name` to the test payload |
| Email validation only checked for `@` presence — `user@domain` or `invalidemail.com` would pass | Replaced with regex `^[^@\s]+@[^@\s]+\.[^@\s]+$` |
| `price < 0` allowed free places (price = 0) despite "positive number" requirement | Changed to `price <= 0` |
| `HBnBFacade` only had user methods; all place, amenity, and review methods were stubs | Implemented all CRUD and helper methods |
| No amenity or review endpoints existed | Created `app/api/v1/amenities.py` and `app/api/v1/reviews.py`, registered in `app/__init__.py` |
