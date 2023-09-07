from dataclasses import dataclass

@dataclass
class Users(object):
    username: str
    password: str

@dataclass
class Shopping(object):
    userid: int
    day_num: int
    item: str
    value: float
    happy: str

        # def __post_init__(self):
    #     if float(self.value) < 0:
    #         raise ValueError("Value cannot be negative")
    #     if not self.item:
    #         raise ValueError("You need to specify the name")
    #     if len(self.username) < 3:
    #         raise ValueError("Username needs at least 3 characters")
    #     if not self.password:
    #         raise ValueError("Password cannot be empty")
