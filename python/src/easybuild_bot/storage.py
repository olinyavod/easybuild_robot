from contextlib import contextmanager
from typing import Iterator, List, Optional
from .models import BotUser, BotGroup
from montydb import MontyClient

_mongo_client: Optional[MontyClient] = None
_db = None

@contextmanager
def db() -> Iterator[object]:
    if _db is None:
        raise RuntimeError("MontyDB is not configured")
    yield _db

def init_db(dir_path: str, db_name: str = "easybuild_bot") -> None:
    global _mongo_client, _db
    _mongo_client = MontyClient(dir_path)
    _db = _mongo_client[db_name]
    # Ensure indexes
    users = _db["users"]
    groups = _db["groups"]
    users.create_index("user_id", unique=True)
    users.create_index("id", unique=True)
    groups.create_index("group_id", unique=True)
    groups.create_index("id", unique=True)

# Users

def add_user(user: BotUser) -> None:
    with db() as database:
        users = database["users"]
        doc = {
            "id": user.id,
            "user_id": user.user_id,
            "user_name": user.user_name,
            "display_name": user.display_name,
            "allowed": bool(user.allowed),
            "is_admin": bool(user.is_admin),
        }
        users.update_one({"user_id": user.user_id}, {"$set": doc}, upsert=True)

def get_user_by_user_id(user_id: int) -> Optional[BotUser]:
    with db() as database:
        users = database["users"]
        doc = users.find_one({"user_id": user_id})
        if not doc:
            return None
        return BotUser(
            id=str(doc.get("id")),
            user_id=int(doc.get("user_id")),
            user_name=str(doc.get("user_name") or ""),
            display_name=doc.get("display_name"),
            allowed=bool(doc.get("allowed", False)),
            is_admin=bool(doc.get("is_admin", False)),
        )

def get_all_users() -> List[BotUser]:
    with db() as database:
        users = database["users"]
        result: List[BotUser] = []
        for doc in users.find({}):
            result.append(
                BotUser(
                    id=str(doc.get("id")),
                    user_id=int(doc.get("user_id")),
                    user_name=str(doc.get("user_name") or ""),
                    display_name=doc.get("display_name"),
                    allowed=bool(doc.get("allowed", False)),
                    is_admin=bool(doc.get("is_admin", False)),
                )
            )
        return result

def update_user_allowed(user_id: int, allowed: bool) -> None:
    with db() as database:
        users = database["users"]
        users.update_one({"user_id": user_id}, {"$set": {"allowed": bool(allowed)}})

def update_user_admin(user_id: int, is_admin: bool) -> None:
    with db() as database:
        users = database["users"]
        users.update_one({"user_id": user_id}, {"$set": {"is_admin": bool(is_admin)}})

# Groups

def add_group(group: BotGroup) -> None:
    with db() as database:
        groups = database["groups"]
        doc = {
            "id": group.id,
            "group_id": group.group_id,
            "group_name": group.group_name,
        }
        groups.update_one({"group_id": group.group_id}, {"$set": doc}, upsert=True)

def get_group_by_group_id(group_id: int) -> Optional[BotGroup]:
    with db() as database:
        groups = database["groups"]
        doc = groups.find_one({"group_id": group_id})
        if not doc:
            return None
        return BotGroup(id=str(doc.get("id")), group_id=int(doc.get("group_id")), group_name=str(doc.get("group_name") or ""))

def get_all_groups() -> List[BotGroup]:
    with db() as database:
        groups = database["groups"]
        result: List[BotGroup] = []
        for doc in groups.find({}):
            result.append(BotGroup(id=str(doc.get("id")), group_id=int(doc.get("group_id")), group_name=str(doc.get("group_name") or "")))
        return result
