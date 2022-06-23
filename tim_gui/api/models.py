from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Type

from pydantic import BaseModel


def convert_to_optional(*schemas: Type[BaseModel]) -> dict[str, object]:
    """
    Turn the fields from schemas into Optional fields
    """
    annotations = {}
    for schema in schemas:
        annotations.update({k: Optional[v] for k, v in schema.__annotations__.items()})

    return annotations


@dataclass
class Login:
    username: str
    password: str


class ItemBase(BaseModel):
    title: str
    bar_code: str
    description: Optional[str] = None
    price: Decimal
    image_path: Optional[str] = None
    quantity: int = 0


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    __annotations__ = convert_to_optional(ItemBase)


class Item(ItemBase):
    id: int
    owner_id: int


class UserBase(BaseModel):
    name: str
    email: str
    is_admin: bool


class User(UserBase):
    id: int
    items: list[Item]


class UserCreate(UserBase):
    password: str


class UserUpdate(UserCreate):
    __annotations__ = convert_to_optional(UserBase, UserCreate)
