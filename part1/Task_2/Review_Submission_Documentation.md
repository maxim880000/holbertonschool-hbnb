# Review Submission API Call — Sequence Documentation

## Purpose
This sequence describes how HBnB processes a **review submission** request through the three architecture layers:
- **Presentation Layer**: receives and returns HTTP messages.
- **Business Logic Layer**: enforces domain rules and orchestration.
- **Persistence Layer**: executes read/write operations against the database.

## API Endpoint
- **Method**: `POST`
- **Path**: `/api/v1/reviews`
- **Request body**:
  - `user_id` (UUID)
  - `place_id` (UUID)
  - `rating` (integer, 1 to 5)
  - `comment` (string, 10 to 500 chars)

## Main Interaction Flow
1. The client sends `POST /api/v1/reviews` to the API endpoint.
2. The API forwards the payload to `ReviewService.submit_review(...)`.
3. `ReviewService` verifies user existence via `UserRepository`.
4. `ReviewService` verifies place existence via `PlaceRepository`.
5. `ReviewService` runs business validations:
   - rating range
   - comment length
   - self-review prevention (`user_id != place.owner_id`)
6. `ReviewService` checks duplicate review policy (`one user per place`).
7. If valid, `ReviewRepository` persists the new review.
8. The service recomputes place average rating.
9. API returns `201 Created` with review payload and aggregate metadata.

## Error Paths Covered in the Diagram
- **404 Not Found**: user or place does not exist.
- **400 Bad Request**: invalid rating/comment or self-review attempt.
- **409 Conflict**: duplicate review detected.

## Layer Responsibilities
- **Presentation Layer (API)**
  - Input transport and response formatting.
  - Maps domain errors to HTTP status codes.
- **Business Logic Layer (ReviewService)**
  - Orchestrates the end-to-end use case.
  - Enforces validation and policy rules.
- **Persistence Layer (Repositories + Database)**
  - Loads referenced entities.
  - Checks duplicate constraints.
  - Persists review and retrieves aggregate rating.

## Outcome
When all checks pass, the system stores a new review, refreshes rating aggregates, and returns a successful creation response. This guarantees consistency between review data and place rating information.
