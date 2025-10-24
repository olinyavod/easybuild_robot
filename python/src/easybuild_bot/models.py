from dataclasses import dataclass
from typing import Optional

@dataclass
class BotUser:
    id: str
    user_id: int
    user_name: str
    display_name: Optional[str] = None
    allowed: bool = False
    is_admin: bool = False

@dataclass
class BotGroup:
    id: str
    group_id: int
    group_name: str
