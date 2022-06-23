from dataclasses import dataclass, field
from decimal import Decimal
from queue import Queue
from typing import Any, Callable, Optional, Type, Union

import requests
from pydantic import BaseModel, parse_obj_as
from requests.models import Response

from .models import (Item, ItemCreate, ItemUpdate, Login, User, UserCreate,
                     UserUpdate)


@dataclass
class RequestResult:
    status_code: int
    data: dict[str, Any]


@dataclass
class Request:
    # result: Optional[RequestResult] = None
    prefix: str = "http://127.0.0.1:8000"
    _request_type_table: dict[str, Callable[..., Response]] = field(
        default_factory=lambda: {
            "POST": requests.post,
            "GET": requests.get,
            "PUT": requests.put,
            "DELETE": requests.delete,
            "HEAD": requests.head,
            "PATCH": requests.patch,
            "OPTIONS": requests.options,
        },
        init=False,
    )

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        request_model=None,
    ):
        if request_model is None:
            data = dict()
        elif isinstance(request_model, BaseModel):
            data = request_model.dict(exclude_none=True)
        else:
            data = request_model.__dict__.copy()

        if issubclass(type(request_model), BaseModel):
            if "price" in data:
                data["price"] = str(data["price"])

            result = self._request_type_table[method](
                f"{self.prefix}{endpoint}", params=params, headers=headers, json=data
            )
        else:
            result = self._request_type_table[method](
                f"{self.prefix}{endpoint}", params=params, headers=headers, data=data
            )

        if 500 <= result.status_code <= 599:
            raise Exception(f"{result.status_code} - {result.reason}")

        result_data = result.json()

        if 400 <= result.status_code <= 499:
            raise Exception(
                f"Error in request:\n\tstatus code: {result.status_code}\n\tDetail: {result_data['detail']}"
            )

        return result_data


class TimAPI(RequestResult):
    # request = Request("http://127.0.0.1:8000", auth="access_token", auth_type="Bearer")

    def __init__(self) -> None:
        self.request = Request()
        self.access_token: Optional[str] = None

    def __repr__(self) -> str:
        return f"TimAPI({self.access_token=}, {self.status_code=}, {self.data=})"

    def login(self, *, username: str, password: str):
        data = self.request.request(
            "POST", "/login/access-token", request_model=Login(username=username, password=password)
        )
        self.token_type: str = data["token_type"]
        self.access_token = data["access_token"]

    def items(self, skip: int = 0, limit: int = 100) -> list[Item]:
        data = self.request.request(
            "GET",
            "/items/",
            params={"skip": skip, "limit": limit},
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return parse_obj_as(list[Item], data)

    def get_item(self, title: str) -> Item:
        data = self.request.request(
            "GET",
            f"/items/{title}",
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return Item(**data)

    def update_item(self, id: int, item: ItemUpdate) -> Item:
        data = self.request.request(
            "PUT",
            f"/items/update/{id}",
            request_model=item,
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return Item(**data)

    def delete_item(self, id: int) -> Item:
        data = self.request.request("DELETE", f"/items/delete/{id}")
        return Item(**data)

    def withdraw_item(self, id: int, quantity: int) -> Item:
        data = self.request.request(
            "GET",
            f"/items/withdraw/{id}",
            params={"quantity": quantity},
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return Item(**data)

    def create_item(self, user_id: int, item: ItemCreate) -> Item:
        data = self.request.request(
            "POST",
            f"/users/{user_id}/items/",
            request_model=item,
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return Item(**data)

    def get_user(self, id: int) -> User:
        data = self.request.request("GET", f"/users/{id}")
        return User(**data)

    def create_user(self, user: UserCreate) -> User:
        data = self.request.request("POST", "/users/register", request_model=user)
        return User(**data)

    def get_user_me(self) -> User:
        data = self.request.request(
            "GET",
            "/users/me",
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return User(**data)

    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        data = self.request.request(
            "GET",
            "/users/",
            params={"skip": skip, "limit": limit},
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return parse_obj_as(list[User], data)

    def update_user(self, id: int, user: UserUpdate) -> User:
        data = self.request.request(
            "PUT",
            f"/users/update/{id}",
            request_model=user,
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return User(**data)

    def update_user_me(self, user: UserUpdate) -> User:
        data = self.request.request(
            "PUT",
            "/users/update/me",
            request_model=user,
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return User(**data)

    def delete_user(self, id: int) -> User:
        data = self.request.request(
            "DELETE",
            f"/users/delete/{id}",
            headers={"Authorization": f"{self.token_type.capitalize()} {self.access_token}"},
        )
        return User(**data)
