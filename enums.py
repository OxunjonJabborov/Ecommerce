from enum import Enum


class Roles(str, Enum):
    ADMIN = "admin"
    SELLER = "seller"
    BUYER = "buyer"


class RegisterRoles(str, Enum):
    SELLER = "seller"
    BUYER = "buyer"
