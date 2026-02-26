# Business Logic Layer - Comprehensive Documentation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Class Specifications](#class-specifications)
5. [Business Logic & Rules](#business-logic--rules)
6. [Relationship Architecture](#relationship-architecture)
7. [Method Specifications](#method-specifications)
8. [Data Flow & Workflows](#data-flow--workflows)
9. [Implementation Strategy](#implementation-strategy)
10. [Security Considerations](#security-considerations)

---

## Executive Summary

### Purpose
This Business Logic Layer (BLL) serves as the core foundation for the HBnB application, a vacation rental platform similar to AirBnB. It encapsulates all domain-specific business rules, data structures, and operations required to manage users, property listings, reviews, and amenities.

### Key Objectives
- **Data Integrity**: Ensure consistent and valid data throughout the system
- **Business Rule Enforcement**: Implement rental platform policies and constraints
- **Separation of Concerns**: Isolate business logic from presentation and data access layers
- **Scalability**: Support growth in users, places, and transactions
- **Maintainability**: Provide clear, well-documented interfaces for future development

### System Context
The BLL sits between the Presentation Layer (API/UI) and the Persistence Layer (database), transforming user actions into validated business operations and managing domain models.

```
┌─────────────────────────────┐
│   Presentation Layer        │
│   (API Endpoints / UI)      │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   Business Logic Layer      │ ◄── This Document
│   (Domain Models & Rules)   │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   Persistence Layer         │
│   (Database / Storage)      │
└─────────────────────────────┘
```

---

## Architecture Overview

### Design Philosophy

The Business Logic Layer follows these architectural principles:

1. **Domain-Driven Design (DDD)**: Classes represent real-world business entities
2. **Inheritance Hierarchy**: Common functionality centralized in `BaseModel`
3. **Single Responsibility**: Each class manages one domain concept
4. **Encapsulation**: Business rules contained within domain objects
5. **Composition over Aggregation**: Proper relationship modeling

### Inheritance Structure

```
BaseModel (Abstract Base Class)
    │
    ├─── User          (Identity & Access)
    ├─── Place         (Property Listings)
    ├─── Review        (User Feedback)
    └─── Amenity       (Property Features)
```

**Design Rationale**:
- **Code Reuse**: Eliminates duplication of common attributes (id, timestamps)
- **Consistency**: All entities follow same lifecycle and serialization patterns
- **Polymorphism**: Enables generic handling of different entity types
- **Maintainability**: Changes to common behavior only need to be made once

---

## Core Components

### Component Overview

| Component | Responsibility | Lifecycle | CRUD Scope |
|-----------|----------------|-----------|------------|
| **BaseModel** | Common entity infrastructure | Abstract - never instantiated | Shared metadata (`crud_profile`) |
| **User** | Identity, authentication, ownership | Created once, updated frequently | C/R/U/D (domain-constrained) |
| **Place** | Property information, availability | Created by users, updated moderately | C/R/U/D |
| **Review** | Feedback and ratings | Created once, rarely updated | C/R/U/D |
| **Amenity** | Feature catalog | System-managed, rarely changes | C/R/U/D |

### Entity State Diagram

```
┌──────────┐    create()     ┌──────────┐    update()     ┌──────────┐
│  Not     │ ──────────────► │  Active  │ ──────────────► │ Modified │
│  Exists  │                 │          │                 │          │
└──────────┘                 └────┬─────┘                 └────┬─────┘
                                  │                            │
                                  │         delete()           │
                                  └────────────┬───────────────┘
                                               ▼
                                         ┌──────────┐
                                         │ Deleted/ │
                                         │ Inactive │
                                         └──────────┘
```

---

## Class Specifications

### 1. BaseModel (Abstract Base Class)

**Purpose**: Provides foundational functionality for all domain entities, ensuring consistency across the system.

#### Attributes

| Attribute | Type | Description | Constraints | Auto-Generated |
|-----------|------|-------------|-------------|----------------|
| `id` | UUID4 | Globally unique identifier | Immutable, Primary Key | Yes (on creation) |
| `created_at` | datetime | UTC timestamp of entity creation | Immutable | Yes (on creation) |
| `updated_at` | datetime | UTC timestamp of last modification | Auto-updated | Yes (on save) |
| `crud_profile` | str | Declares supported CRUD operations for the entity | Default `CRUD`, inherited by all subclasses | Yes (default value) |

#### Methods

##### `save()`
- **Purpose**: Persists the current state of the entity to the database
- **Behavior**: 
  - Updates `updated_at` to current UTC timestamp
  - Validates entity state before persistence
  - Triggers database write operation
- **Returns**: None
- **Raises**: `ValidationError` if entity state is invalid

##### `to_dict()`
- **Purpose**: Serializes entity to dictionary format for JSON API responses
- **Behavior**:
  - Converts all attributes to JSON-serializable types
  - Formats datetime objects to ISO 8601 strings
  - Excludes private/internal attributes (prefixed with `_`)
- **Returns**: `dict` with all public attributes
- **Example Output**:
```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-02-18T10:30:00Z",
    "updated_at": "2026-02-18T12:45:00Z"
}
```

##### `update(**kwargs)`
- **Purpose**: Updates multiple attributes in a single operation
- **Parameters**: `**kwargs` - Key-value pairs of attributes to update
- **Behavior**:
  - Validates each attribute before assignment
  - Ignores attempts to update protected fields (id, created_at)
  - Calls `save()` automatically after successful update
- **Returns**: `bool` - True if successful
- **Raises**: `ValidationError` for invalid attributes

**Business Rules**:
- `id` is generated once and never changes
- All timestamps use UTC to avoid timezone issues
- `updated_at` automatically reflects last modification
- Cannot instantiate BaseModel directly (abstract class)

---

### 2. User

**Purpose**: Represents a registered user account with authentication, profile management, and administrative capabilities.

#### Attributes

| Attribute | Type | Description | Constraints | Default |
|-----------|------|-------------|-------------|---------|
| `first_name` | str | User's given name | Required, 1-50 chars, alphabetic | None |
| `last_name` | str | User's family name | Required, 1-50 chars, alphabetic | None |
| `email` | str | Email address (login identifier) | Required, unique, valid email format | None |
| `password_hash` | str | Hashed password | Required, bcrypt hash, never plain text | None |
| `is_admin` | bool | Administrative privileges flag | True for admins, False for regular users | False |

**Inherited**: `id`, `created_at`, `updated_at` from BaseModel

#### Methods

##### `register()`
- **Purpose**: Creates a new user account with validation
- **Business Logic**:
  1. Validate email uniqueness (query existing users)
  2. Validate password strength (min 8 chars, mixed case, numbers)
  3. Hash password using bcrypt (never store plain text)
  4. Set `is_admin` to False by default
  5. Generate UUID and timestamps
  6. Persist to database
- **Returns**: `bool` - True if registration successful
- **Raises**: 
  - `EmailAlreadyExistsError` if email is taken
  - `WeakPasswordError` if password doesn't meet requirements

##### `update_profile(**kwargs)`
- **Purpose**: Allows users to modify their profile information
- **Parameters**: `**kwargs` - Attributes to update (first_name, last_name, email)
- **Business Logic**:
  - Validates new email uniqueness if email is being changed
  - Prevents modification of `is_admin` (only system can set this)
  - Requires re-authentication for sensitive changes
- **Returns**: `bool` - True if successful
- **Security**: Email changes may require verification

##### `change_password(old_password, new_password)`
- **Purpose**: Securely changes user password
- **Parameters**:
  - `old_password`: str - Current password for verification
  - `new_password`: str - New password to set
- **Business Logic**:
  1. Authenticate old password against stored hash
  2. Validate new password strength
  3. Ensure new password differs from old password
  4. Hash new password with bcrypt
  5. Update `password_hash` field
- **Returns**: `bool` - True if successful
- **Raises**: `AuthenticationError` if old password is incorrect

##### `delete()`
- **Purpose**: Deactivates or removes user account
- **Business Logic**:
  - **Soft Delete** (Recommended): Set `is_active=False` flag instead of removing
  - Check for owned places - must transfer ownership or delete places first
  - Optionally anonymize user reviews instead of deleting
  - Log deletion for audit trail
- **Returns**: `bool` - True if successful
- **Raises**: `CannotDeleteError` if user owns active places

##### `authenticate(password)`
- **Purpose**: Verifies user credentials for login
- **Parameters**: `password`: str - Plain text password to verify
- **Business Logic**:
  1. Retrieve user by email
  2. Compare provided password against stored hash using bcrypt
  3. Log authentication attempts (for security monitoring)
  4. Implement rate limiting to prevent brute force attacks
- **Returns**: `bool` or JWT token - True/token if authenticated
- **Security**: Should be used with session management or JWT tokens

#### Business Rules

1. **Email Uniqueness**: No two users can have the same email address
2. **Password Security**: 
   - Minimum 8 characters
   - Must contain: uppercase, lowercase, digit, special character
   - Never stored in plain text (bcrypt hash only)
   - Password changes require old password verification
3. **Admin Privileges**: 
   - Only system administrators can set `is_admin=True`
   - Regular users cannot elevate their own privileges
4. **Account Deletion**:
   - Prefer soft deletion to maintain data integrity
   - Must not own active places before deletion
   - Reviews can be kept but anonymized
5. **Profile Updates**:
   - Email changes require email verification
   - Name changes have no restrictions beyond format validation

---

### 3. Place

**Purpose**: Represents a property listing available for rental, including all descriptive information, pricing, location, and availability status.

#### Attributes

| Attribute | Type | Description | Constraints | Default |
|-----------|------|-------------|-------------|---------|
| `title` | str | Property name/headline | Required, 5-100 chars | None |
| `description` | str | Detailed property description | Optional, max 2000 chars | "" |
| `price_per_night` | float | Nightly rental rate | Required, >= 1.00, 2 decimals | None |
| `latitude` | float | GPS coordinate (latitude) | Required, -90.0 to 90.0 | None |
| `longitude` | float | GPS coordinate (longitude) | Required, -180.0 to 180.0 | None |
| `max_guests` | int | Maximum occupancy | Required, 1-50 | 1 |
| `is_available` | bool | Current availability status | True if bookable | True |

**Inherited**: `id`, `created_at`, `updated_at` from BaseModel

**Relationships**:
- **Owner**: Reference to User (foreign key: owner_id, not shown in diagram but implicit)
- **Reviews**: Collection of Review objects
- **Amenities**: Many-to-many with Amenity objects

#### Methods

##### `create(owner_id, **attributes)`
- **Purpose**: Creates a new place listing
- **Parameters**:
  - `owner_id`: UUID4 - ID of the user creating the place
  - `**attributes`: All required place attributes
- **Business Logic**:
  1. Validate owner exists and is authenticated
  2. Validate all required fields are provided
  3. Validate geographic coordinates are valid
  4. Validate price is positive and reasonable (<= 10000)
  5. Set `is_available=True` by default
  6. Link to owner via `owner_id`
- **Returns**: Place object
- **Raises**: `ValidationError` for invalid data

##### `update(**kwargs)`
- **Purpose**: Updates place information
- **Parameters**: `**kwargs` - Attributes to modify
- **Business Logic**:
  - Only owner or admin can update
  - Cannot change `owner_id` (permanent assignment)
  - Validates new values before applying
  - Logs all changes for audit trail
- **Returns**: `bool` - True if successful
- **Authorization**: Requires ownership verification

##### `delete()`
- **Purpose**: Removes place listing
- **Business Logic**:
  - Check if place has active bookings (if booking system exists)
  - Delete or archive associated reviews (cascade delete)
  - Remove amenity associations (from junction table)
  - Soft delete preferred: set `is_available=False` and `deleted_at`
- **Returns**: `bool` - True if successful
- **Authorization**: Only owner or admin can delete

##### `set_availability(is_available)`
- **Purpose**: Toggle place availability for booking
- **Parameters**: `is_available`: bool - True to make bookable, False otherwise
- **Business Logic**:
  - Used to temporarily hide listings (maintenance, off-season)
  - Does not delete the place, just hides from search
  - Can be toggled by owner at any time
- **Returns**: `bool` - True if successful
- **Use Case**: Owner goes on vacation or property under renovation

##### `list_amenities()`
- **Purpose**: Retrieves all amenities associated with this place
- **Business Logic**:
  - Queries the many-to-many relationship via junction table
  - Returns amenity objects with full details
- **Returns**: `List[Amenity]` - List of amenity objects
- **Performance**: Consider caching for frequently accessed places

##### `add_amenity(amenity_id)`
- **Purpose**: Associates an amenity with this place
- **Parameters**: `amenity_id`: UUID4 - ID of amenity to add
- **Business Logic**:
  1. Verify amenity exists in system
  2. Check if already associated (prevent duplicates)
  3. Create entry in `place_amenities` junction table
  4. Update `updated_at` timestamp
- **Returns**: `bool` - True if successful
- **Idempotent**: Adding existing amenity has no effect

##### `remove_amenity(amenity_id)`
- **Purpose**: Removes amenity association
- **Parameters**: `amenity_id`: UUID4 - ID of amenity to remove
- **Business Logic**:
  1. Verify association exists
  2. Delete entry from junction table
  3. Update `updated_at` timestamp
- **Returns**: `bool` - True if successful
- **Safe**: Removing non-existent amenity has no effect

##### `get_average_rating()`
- **Purpose**: Calculates average rating from all reviews
- **Business Logic**:
  1. Query all reviews for this place
  2. Compute average of all `rating` values
  3. Return rounded to 1 decimal place
  4. Return 0.0 if no reviews exist
- **Returns**: `float` - Average rating (0.0 to 5.0)
- **Caching**: Should cache result and invalidate on new review

#### Business Rules

1. **Ownership**:
   - Every place must have one owner (user)
   - Owner cannot be changed after creation
   - Owner can have multiple places
2. **Geographic Validation**:
   - Latitude: -90° to +90° (South to North)
   - Longitude: -180° to +180° (West to East)
   - Coordinates must be precise (valid decimal format)
3. **Pricing**:
   - Must be positive (>= 1.00)
   - Maximum reasonable price: $10,000/night
   - Stored with exactly 2 decimal places
   - Currency assumed to be USD (or configurable)
4. **Availability**:
   - New places are available by default
   - Unavailable places hidden from search results
   - Does not affect existing bookings (if implemented)
5. **Amenities**:
   - Place can have 0 to unlimited amenities
   - Same amenity cannot be added twice
   - Amenities are system-wide (not place-specific)
6. **Reviews**:
   - Place can receive unlimited reviews
   - Average rating updates automatically
   - Reviews cascade delete when place is deleted
7. **Capacity**:
   - Minimum 1 guest, maximum 50 guests
   - Should match actual property capacity

---

### 4. Review

**Purpose**: Captures user feedback and ratings for places they have experienced, providing social proof and quality indicators.

#### Attributes

| Attribute | Type | Description | Constraints | Default |
|-----------|------|-------------|-------------|---------|
| `rating` | int | Numerical rating score | Required, 1-5 inclusive | None |
| `comment` | str | Written review text | Required, 10-500 chars | None |

**Inherited**: `id`, `created_at`, `updated_at` from BaseModel

**Relationships** (implicit foreign keys):
- **Author**: Reference to User (`user_id`)
- **Subject**: Reference to Place (`place_id`)

#### Methods

##### `create(user_id, place_id, rating, comment)`
- **Purpose**: Submits a new review for a place
- **Parameters**:
  - `user_id`: UUID4 - ID of user writing review
  - `place_id`: UUID4 - ID of place being reviewed
  - `rating`: int - Rating score (1-5)
  - `comment`: str - Review text
- **Business Logic**:
  1. Validate user exists and is authenticated
  2. Validate place exists
  3. **Prevent self-review**: User cannot review their own place
  4. Validate rating is 1-5
  5. Validate comment length (10-500 chars)
  6. Check for duplicate review (optional: one review per user per place)
  7. Create review record
  8. Update place's average rating cache
- **Returns**: Review object
- **Raises**: 
  - `SelfReviewError` if user owns the place
  - `ValidationError` for invalid data
  - `DuplicateReviewError` if policy enforced

##### `update(**kwargs)`
- **Purpose**: Allows author to edit their review
- **Parameters**: `**kwargs` - Attributes to update (rating, comment)
- **Business Logic**:
  - Only author can update (verify user_id matches)
  - Cannot change place being reviewed
  - Revalidate rating and comment
  - Update place's average rating if rating changed
  - Track edit history (optional: store original version)
- **Returns**: `bool` - True if successful
- **Authorization**: Author only (or admin)
- **Time Limit**: Consider 7-day edit window

##### `delete()`
- **Purpose**: Removes a review
- **Business Logic**:
  - Only author or admin can delete
  - Update place's average rating and review count
  - Consider soft delete to preserve data
  - Log deletion for moderation purposes
- **Returns**: `bool` - True if successful
- **Authorization**: Author or admin

##### `validate_rating()`
- **Purpose**: Ensures rating is within valid range
- **Business Logic**:
  - Check rating is integer
  - Check value is 1, 2, 3, 4, or 5
  - Called automatically before save/update
- **Returns**: `bool` - True if valid
- **Raises**: `ValidationError` if rating invalid

#### Business Rules

1. **Rating Scale**:
   - 1 = Poor
   - 2 = Fair
   - 3 = Good
   - 4 = Very Good
   - 5 = Excellent
   - Must be integer (no decimal ratings)
2. **Self-Review Prevention**:
   - Users cannot review places they own
   - Prevents artificial rating inflation
3. **Comment Requirements**:
   - Minimum 10 characters (enforce meaningful feedback)
   - Maximum 500 characters (encourage conciseness)
   - Must be text (no HTML, scripts)
4. **Review Authenticity**:
   - Optionally require verified booking before review
   - One review per user per place (configurable)
5. **Moderation**:
   - Reviews should be screened for profanity
   - Admins can delete inappropriate reviews
   - Consider flagging system for user reports
6. **Immutability Considerations**:
   - Reviews can be edited within time window (7 days)
   - After time window, reviews are immutable
   - All edits logged for transparency
7. **Impact on Place**:
   - New review triggers average rating recalculation
   - Place's `updated_at` should NOT change (review is separate entity)

---

### 5. Amenity

**Purpose**: Represents features, facilities, or services that a place can offer (e.g., WiFi, parking, pool, kitchen).

#### Attributes

| Attribute | Type | Description | Constraints | Default |
|-----------|------|-------------|-------------|---------|
| `name` | str | Display name of amenity | Required, unique, 2-50 chars | None |
| `description` | str | Detailed explanation | Optional, max 200 chars | "" |

**Inherited**: `id`, `created_at`, `updated_at` from BaseModel

**Relationships**:
- **Places**: Many-to-many with Place objects (places offering this amenity)

#### Methods

##### `create(name, description="")`
- **Purpose**: Adds a new amenity to the system catalog
- **Parameters**:
  - `name`: str - Amenity name (must be unique)
  - `description`: str - Optional description
- **Business Logic**:
  1. Validate name uniqueness (case-insensitive)
  2. Sanitize name (trim, capitalize properly)
  3. Validate description length
  4. Create amenity record
- **Returns**: Amenity object
- **Raises**: `DuplicateAmenityError` if name exists
- **Authorization**: Admin only (system-managed)

##### `update(**kwargs)`
- **Purpose**: Modifies amenity information
- **Parameters**: `**kwargs` - Attributes to update
- **Business Logic**:
  - Validate name uniqueness if name is changing
  - Update all places using this amenity (cached data)
- **Returns**: `bool` - True if successful
- **Authorization**: Admin only

##### `delete()`
- **Purpose**: Removes amenity from system
- **Business Logic**:
  1. Check if any places are using this amenity
  2. If yes, remove all associations from junction table
  3. Delete amenity record
  4. Consider soft delete for historical data
- **Returns**: `bool` - True if successful
- **Authorization**: Admin only
- **Warning**: Affects all places using this amenity

#### Business Rules

1. **Uniqueness**:
   - Amenity names must be unique (case-insensitive)
   - Prevents duplicates like "WiFi" and "wifi"
2. **System-Managed**:
   - Only administrators can create/update/delete amenities
   - Regular users can only select from existing amenities
3. **Standardization**:
   - Use conventional names (WiFi, not "Internet")
   - Consider categorization (Essential, Entertainment, Safety)
4. **Reusability**:
   - Amenities are global resources
   - Same amenity can be used by unlimited places
5. **Localization**:
   - Consider multi-language support for international platforms
   - Store translations separately or use i18n keys

**Common Amenity Examples**:
- Essential: WiFi, Air Conditioning, Heating, Hot Water
- Kitchen: Full Kitchen, Kitchenette, Coffee Maker, Dishwasher
- Entertainment: TV, Cable, Streaming Services, Game Console
- Outdoor: Pool, Hot Tub, BBQ Grill, Garden
- Safety: Smoke Detector, Carbon Monoxide Detector, First Aid Kit
- Accessibility: Wheelchair Accessible, Elevator, Step-Free Entry

---

## Business Logic & Rules

### Cross-Entity Business Rules

#### 1. User-Place Ownership Rules
```python
# A user can own multiple places
user.places → List[Place]  # 0 to unlimited

# A place has exactly one owner
place.owner → User  # 1 and only 1

# Constraint: Cannot transfer ownership (permanent assignment)
# Constraint: Must delete or reassign places before deleting user
```

#### 2. User-Review Authorship Rules
```python
# A user can write multiple reviews (for different places)
user.reviews → List[Review]  # 0 to unlimited

# A review has exactly one author
review.author → User  # 1 and only 1

# Constraint: User cannot review their own places
if review.user_id == place.owner_id:
    raise SelfReviewError()

# Constraint: One review per user per place (optional policy)
existing_review = Review.query.filter_by(
    user_id=user_id, 
    place_id=place_id
).first()
if existing_review:
    raise DuplicateReviewError()
```

#### 3. Place-Review Target Rules
```python
# A place can receive multiple reviews
place.reviews → List[Review]  # 0 to unlimited

# A review targets exactly one place
review.place → Place  # 1 and only 1

# Derived data: Average rating
place.average_rating = sum(r.rating for r in place.reviews) / len(place.reviews)

# Constraint: Reviews cascade delete with place
on_delete_place → delete_all_associated_reviews()
```

#### 4. Place-Amenity Association Rules
```python
# A place can offer multiple amenities
place.amenities → List[Amenity]  # 0 to unlimited

# An amenity can be offered by multiple places
amenity.places → List[Place]  # 0 to unlimited

# Implementation: Junction table 'place_amenities'
# Columns: place_id, amenity_id, created_at
# Primary Key: (place_id, amenity_id)

# Constraint: No duplicate associations
# Constraint: Both place and amenity must exist (referential integrity)
```

---

## Relationship Architecture

### Relationship Type Explanation

The diagram uses UML notation to indicate relationship types:

#### 1. Composition (`*--`)
**Symbol**: Solid diamond with solid line

**Used for**: User-Place, User-Review

**Meaning**: 
- Strong ownership relationship
- Child cannot exist without parent
- Lifecycle dependency

**Example**:
```python
User "1" *-- "0..*" Place : owns
```
- Places are created BY users and FOR users
- If user is deleted, their places should be handled carefully
- Strong coupling: owner_id is required field

#### 2. Aggregation (`o--`)
**Symbol**: Hollow diamond with solid line

**Used for**: Place-Amenity

**Meaning**:
- Weak association
- Children can exist independently
- Shared resources

**Example**:
```python
Place "0..*" o-- "0..*" Amenity : offers
```
- Amenities exist independently of any place
- Multiple places can share same amenity
- Deleting a place doesn't delete amenities

### Relationship Cardinality Details

| Relationship | From | To | Cardinality | Meaning |
|--------------|------|-----|-------------|---------|
| Ownership | User | Place | 1 : 0..* | One user owns zero or more places |
| Authorship | User | Review | 1 : 0..* | One user writes zero or more reviews |
| Reception | Place | Review | 1 : 0..* | One place receives zero or more reviews |
| Offering | Place | Amenity | 0..* : 0..* | Many-to-many association |

### Database Implementation

#### Foreign Key Relationships

```sql
-- Places table
CREATE TABLE places (
    id UUID PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR(100) NOT NULL,
    -- ... other fields
);

-- Reviews table
CREATE TABLE reviews (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    place_id UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL CHECK (LENGTH(comment) >= 10 AND LENGTH(comment) <= 500),
    -- ... other fields
);

-- Junction table for many-to-many
CREATE TABLE place_amenities (
    place_id UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    amenity_id UUID NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (place_id, amenity_id)
);
```

#### Deletion Cascades

| Entity | Deletion Strategy | Rationale |
|--------|------------------|-----------|
| **User** | RESTRICT if owns places | Prevent data loss, require cleanup |
| **Place** | CASCADE reviews | Reviews meaningless without place |
| **Review** | CASCADE from user/place | Either deletion removes review |
| **Amenity** | CASCADE associations only | Amenity itself preserved |

---

## Method Specifications

### CRUD Operations Summary

| Class | Create | Read | Update | Delete |
|-------|--------|------|--------|--------|
| **User** | `register()` | Inherited query | `update_profile()` | `delete()` |
| **Place** | `create()` | Inherited query | `update()` | `delete()` |
| **Review** | `create()` | Inherited query | `update()` | `delete()` |
| **Amenity** | `create()` | Inherited query | `update()` | `delete()` |

### Specialized Methods

#### User-Specific
- `authenticate(password)` - Login verification
- `change_password(old, new)` - Secure password update

#### Place-Specific
- `set_availability(bool)` - Toggle booking availability
- `list_amenities()` - Get all associated amenities
- `add_amenity(id)` - Associate amenity
- `remove_amenity(id)` - Disassociate amenity
- `get_average_rating()` - Compute rating from reviews

#### Review-Specific
- `validate_rating()` - Ensure 1-5 range

---

## Data Flow & Workflows

### Workflow 1: User Registration

```
┌─────────────┐
│ User enters │
│ credentials │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ User.register() │
└──────┬──────────┘
       │
       ├─► Validate email uniqueness
       ├─► Validate password strength
       ├─► Hash password (bcrypt)
       ├─► Set is_admin = False
       ├─► Generate UUID & timestamps
       │
       ▼
┌─────────────────┐
│   Save to DB    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Return success │
│ or error detail │
└─────────────────┘
```

### Workflow 2: Create Place Listing

```
┌──────────────┐
│ Owner fills  │
│ place form   │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ Place.create()      │
└──────┬──────────────┘
       │
       ├─► Verify owner is authenticated
       ├─► Validate title (5-100 chars)
       ├─► Validate price (>= 1.00)
       ├─► Validate coordinates (lat/lon ranges)
       ├─► Validate max_guests (1-50)
       ├─► Set is_available = True
       ├─► Link to owner (owner_id)
       │
       ▼
┌─────────────────┐
│   Save to DB    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Return Place ID │
└─────────────────┘
```

### Workflow 3: Submit Review

```
┌──────────────────┐
│ User writes      │
│ review & rating  │
└──────┬───────────┘
       │
       ▼
┌─────────────────────┐
│ Review.create()     │
└──────┬──────────────┘
       │
       ├─► Verify user authenticated
       ├─► Verify place exists
       ├─► Check NOT self-review (user_id != owner_id)
       ├─► Validate rating (1-5)
       ├─► Validate comment (10-500 chars)
       ├─► Check for duplicate review (optional)
       │
       ▼
┌─────────────────────┐
│   Save review       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────┐
│ Update place's average  │
│ rating (cache/compute)  │
└──────┬──────────────────┘
       │
       ▼
┌──────────────────┐
│ Notify place     │
│ owner (optional) │
└──────────────────┘
```

### Workflow 4: Add Amenity to Place

```
┌──────────────────┐
│ Owner selects    │
│ amenity to add   │
└──────┬───────────┘
       │
       ▼
┌─────────────────────────┐
│ Place.add_amenity(id)   │
└──────┬──────────────────┘
       │
       ├─► Verify ownership or admin
       ├─► Verify amenity exists in catalog
       ├─► Check if already associated
       │   (if yes, return success idempotently)
       │
       ▼
┌──────────────────────────────┐
│ Insert into place_amenities  │
│ (place_id, amenity_id)       │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────┐
│ Update place's   │
│ updated_at       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Return success   │
└──────────────────┘
```

---

## Implementation Strategy

### Phase 1: Foundation (Week 1-2)

**Objective**: Implement core infrastructure

1. **BaseModel Implementation**
   - Create abstract base class
   - Implement UUID generation
   - Implement timestamp management
   - Implement `save()`, `to_dict()`, `update()` methods
   - Write unit tests for BaseModel

2. **Database Setup**
   - Design database schema
   - Create migration scripts
   - Set up indexes for performance
   - Configure connection pooling

### Phase 2: Core Entities (Week 3-4)

**Objective**: Implement main business entities

1. **User Entity**
   - Extend BaseModel
   - Implement authentication methods
   - Set up password hashing (bcrypt)
   - Implement user CRUD operations
   - Write unit tests

2. **Place Entity**
   - Extend BaseModel
   - Implement place CRUD operations
   - Implement availability toggle
   - Write unit tests

3. **Amenity Entity**
   - Extend BaseModel
   - Implement amenity CRUD operations
   - Create initial amenity catalog
   - Write unit tests

### Phase 3: Relationships (Week 5)

**Objective**: Implement entity relationships

1. **User-Place Ownership**
   - Add owner_id foreign key to Place
   - Implement `user.get_places()`
   - Implement `place.get_owner()`
   - Add ownership verification

2. **Place-Amenity Association**
   - Create junction table
   - Implement `place.add_amenity()`
   - Implement `place.remove_amenity()`
   - Implement `place.list_amenities()`

### Phase 4: Reviews (Week 6)

**Objective**: Implement review system

1. **Review Entity**
   - Extend BaseModel
   - Implement review CRUD operations
   - Implement rating validation
   - Add self-review prevention

2. **Review Relationships**
   - Link reviews to users
   - Link reviews to places
   - Implement `place.get_average_rating()`

### Phase 5: Business Logic (Week 7)

**Objective**: Enforce business rules

1. **Validation Layer**
   - Implement all constraint validations
   - Add custom validators
   - Implement error handling

2. **Business Rules**
   - Enforce self-review prevention
   - Implement deletion cascades
   - Add ownership verification

### Phase 6: Testing & Optimization (Week 8)

**Objective**: Ensure quality and performance

1. **Testing**
   - Unit tests for all classes
   - Integration tests for workflows
   - Edge case testing
   - Performance testing

2. **Optimization**
   - Add database indexes
   - Implement caching (average ratings)
   - Optimize N+1 query problems
   - Add connection pooling

---

## Security Considerations

### Authentication & Authorization

1. **Password Security**
   ```python
   # Use bcrypt for password hashing
   import bcrypt
   
   hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
   # Store hashed, never plain text
   
   # Verify password
   is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
   ```

2. **Session Management**
   - Use JWT tokens or secure sessions
   - Implement token expiration
   - Support token refresh
   - Logout invalidates tokens

3. **Role-Based Access Control (RBAC)**
   ```python
   def require_owner_or_admin(user, place):
       if user.id != place.owner_id and not user.is_admin:
           raise UnauthorizedError()
   ```

### Input Validation

1. **SQL Injection Prevention**
   - Use parameterized queries
   - Use ORM (SQLAlchemy) query builders
   - Never concatenate user input into SQL

2. **XSS Prevention**
   - Sanitize all text inputs (especially reviews)
   - Escape HTML in outputs
   - Use Content Security Policy headers

3. **Email Validation**
   ```python
   import re
   
   EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
   
   def is_valid_email(email):
       return re.match(EMAIL_REGEX, email) is not None
   ```

### Data Protection

1. **Personal Data**
   - Hash passwords (never store plain text)
   - Encrypt sensitive data at rest
   - Use HTTPS for data in transit
   - Implement GDPR compliance (data export, right to deletion)

2. **Rate Limiting**
   ```python
   # Prevent brute force attacks
   @rate_limit(max_attempts=5, window=300)  # 5 attempts per 5 minutes
   def authenticate(email, password):
       # ...
   ```

3. **Audit Logging**
   - Log all authentication attempts
   - Log all data modifications
   - Log admin actions
   - Retain logs for security analysis

### Common Vulnerabilities to Prevent

| Vulnerability | Prevention |
|---------------|------------|
| SQL Injection | Parameterized queries, ORM |
| XSS | Input sanitization, output escaping |
| CSRF | CSRF tokens, SameSite cookies |
| Brute Force | Rate limiting, account lockout |
| Session Hijacking | Secure cookies, HTTPS only |
| Privilege Escalation | Proper authorization checks |

---

## Appendix

### A. Validation Rules Reference

```python
# User validations
USER_VALIDATIONS = {
    'first_name': {
        'min_length': 1,
        'max_length': 50,
        'pattern': r'^[A-Za-z\s\-]+$'
    },
    'last_name': {
        'min_length': 1,
        'max_length': 50,
        'pattern': r'^[A-Za-z\s\-]+$'
    },
    'email': {
        'max_length': 255,
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'unique': True
    },
    'password': {
        'min_length': 8,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_digit': True,
        'require_special': True
    }
}

# Place validations
PLACE_VALIDATIONS = {
    'title': {
        'min_length': 5,
        'max_length': 100
    },
    'description': {
        'max_length': 2000
    },
    'price_per_night': {
        'min': 1.00,
        'max': 10000.00,
        'decimals': 2
    },
    'latitude': {
        'min': -90.0,
        'max': 90.0
    },
    'longitude': {
        'min': -180.0,
        'max': 180.0
    },
    'max_guests': {
        'min': 1,
        'max': 50
    }
}

# Review validations
REVIEW_VALIDATIONS = {
    'rating': {
        'min': 1,
        'max': 5,
        'type': 'integer'
    },
    'comment': {
        'min_length': 10,
        'max_length': 500
    }
}

# Amenity validations
AMENITY_VALIDATIONS = {
    'name': {
        'min_length': 2,
        'max_length': 50,
        'unique': True
    },
    'description': {
        'max_length': 200
    }
}
```

### B. Error Handling

```python
# Custom exceptions
class BusinessLogicError(Exception):
    """Base exception for business logic errors"""
    pass

class ValidationError(BusinessLogicError):
    """Raised when data validation fails"""
    pass

class AuthenticationError(BusinessLogicError):
    """Raised when authentication fails"""
    pass

class AuthorizationError(BusinessLogicError):
    """Raised when user lacks permission"""
    pass

class EmailAlreadyExistsError(ValidationError):
    """Raised when email is already registered"""
    pass

class SelfReviewError(BusinessLogicError):
    """Raised when user attempts to review own place"""
    pass

class DuplicateReviewError(BusinessLogicError):
    """Raised when user attempts duplicate review"""
    pass
```

### C. Performance Optimization

```python
# Caching strategy for average ratings
from functools import lru_cache
from datetime import datetime, timedelta

class Place:
    _rating_cache = {}
    _cache_ttl = timedelta(minutes=15)
    
    def get_average_rating(self):
        cache_key = f"place_{self.id}_rating"
        cached = self._rating_cache.get(cache_key)
        
        if cached and datetime.utcnow() - cached['time'] < self._cache_ttl:
            return cached['value']
        
        # Compute from database
        ratings = [r.rating for r in self.reviews]
        avg = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Cache result
        self._rating_cache[cache_key] = {
            'value': avg,
            'time': datetime.utcnow()
        }
        
        return avg
    
    def invalidate_rating_cache(self):
        """Call when new review added"""
        cache_key = f"place_{self.id}_rating"
        self._rating_cache.pop(cache_key, None)
```

---

## Conclusion

This Business Logic Layer provides a robust foundation for the HBnB application with:

✅ **Well-defined entities** with clear responsibilities  
✅ **Strong business rules** preventing data inconsistencies  
✅ **Flexible relationships** supporting complex queries  
✅ **Security-first design** protecting user data  
✅ **Scalable architecture** ready for growth  
✅ **Comprehensive validation** ensuring data quality  
✅ **Audit trail capabilities** for compliance  
✅ **Performance considerations** through caching and indexing  

### Key Takeaways

1. **BaseModel** centralizes common functionality, reducing code duplication
2. **User** manages authentication and ownership with secure password handling
3. **Place** represents property listings with geographic and pricing data
4. **Review** provides social proof with ratings and comments
5. **Amenity** catalogs reusable features across properties
6. **Relationships** are properly modeled with appropriate cardinalities
7. **Business rules** enforce platform policies automatically
8. **Security** is embedded throughout with validation and authorization

### Next Steps for Implementation

1. Set up development environment with Python 3.8+
2. Install dependencies (SQLAlchemy, bcrypt, Flask/FastAPI)
3. Implement BaseModel first as foundation
4. Build entities incrementally (User → Place → Amenity → Review)
5. Add relationships and constraints
6. Write comprehensive tests
7. Optimize with indexes and caching
8. Deploy to staging environment for testing

**Document Version**: 1.0  
**Last Updated**: February 18, 2026  
**Status**: Complete and ready for implementation
