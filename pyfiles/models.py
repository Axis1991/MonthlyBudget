from dataclasses import dataclass
from datetime import datetime

@dataclass
class Users(object):
    username: str
    password: str
    id: int|None = None # domyślne na końcu

@dataclass
class Shopping(object):
    userid: int
    date: datetime
    value: float
    item: str
    happy: str
    itemID: int|None = None

        # def __post_init__(self):
    #     if float(self.value) < 0:
    #         raise ValueError("Value cannot be negative")
    #     if not self.item:
    #         raise ValueError("You need to specify the name")
    #     if len(self.username) < 3:
    #         raise ValueError("Username needs at least 3 characters")
    #     if not self.password:
    #         raise ValueError("Password cannot be empty")
