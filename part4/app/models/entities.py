from __future__ import annotations

from dataclasses import dataclass, field

from app.models.base_model import BaseModel


@dataclass
class User(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: str = ""

    def __post_init__(self) -> None:
        if not self.first_name or not self.last_name:
            raise ValueError("first_name and last_name are required")
        if "@" not in self.email:
            raise ValueError("email must be valid")


@dataclass
class Amenity(BaseModel):
    name: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")


@dataclass
class Place(BaseModel):
    title: str = ""
    description: str = ""
    price: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    owner_id: str = ""
    amenity_ids: list[str] = field(default_factory=list)
    review_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("title is required")
        if self.price < 0:
            raise ValueError("price must be >= 0")
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")
        if not self.owner_id:
            raise ValueError("owner_id is required")


@dataclass
class Review(BaseModel):
    text: str = ""
    user_id: str = ""
    place_id: str = ""

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError("text is required")
        if not self.user_id:
            raise ValueError("user_id is required")
        if not self.place_id:
            raise ValueError("place_id is required")