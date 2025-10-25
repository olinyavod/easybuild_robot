import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Setup paths for importing src.easybuild_bot package
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]  # .../easybuild_bot
PYTHON_ROOT = REPO_ROOT / 'python'
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.easybuild_bot.storage import Storage
from src.easybuild_bot.models import BotUser, BotGroup  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Import JSON (Hive export) to MontyDB')
    parser.add_argument('--file', dest='file', type=str, default=str(REPO_ROOT / 'data/export/hive_export.json'), help='Path to JSON file with Hive export')
    parser.add_argument('--monty-dir', dest='monty_dir', type=str, default=str(REPO_ROOT / 'data/monty'), help='Directory for MontyDB')
    parser.add_argument('--monty-db', dest='monty_db', type=str, default=os.getenv('MONTYDB_DB', 'easybuild_bot'), help='MontyDB database name')
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    json_path = Path(args.file)
    if not json_path.exists():
        raise FileNotFoundError(f'JSON not found: {json_path}')

    monty_dir = Path(args.monty_dir)
    monty_dir.mkdir(parents=True, exist_ok=True)

    # Initialize storage with new DI architecture
    storage = Storage(dir_path=str(monty_dir), db_name=args.monty_db)

    with json_path.open('r', encoding='utf-8') as f:
        data = json.load(f)

    users = data.get('users', []) or []
    groups = data.get('groups', []) or []

    users_count = 0
    for u in users:
        # Map fields from Hive (camelCase) to Python models (snake_case)
        bot_user = BotUser(
            id=str(u.get('id')),
            user_id=int(u.get('userId')),
            user_name=str(u.get('userName') or ''),
            display_name=u.get('displayName'),
            allowed=bool(u.get('allowed', False)),
            is_admin=bool(u.get('isAdmin', False)),
        )
        storage.add_user(bot_user)
        users_count += 1

    groups_count = 0
    for g in groups:
        bot_group = BotGroup(
            id=str(g.get('id')),
            group_id=int(g.get('groupId')),
            group_name=str(g.get('groupName') or ''),
        )
        storage.add_group(bot_group)
        groups_count += 1

    print(f'Import completed. Users: {users_count}, Groups: {groups_count}')


if __name__ == '__main__':
    main()
