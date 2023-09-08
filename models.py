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
