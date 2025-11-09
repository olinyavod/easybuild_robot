#!/usr/bin/env python3
"""
Скрипт для быстрой привязки проектов к группам.
"""

from src.easybuild_bot.storage import Storage
import os

data_dir = os.path.join(os.getcwd(), 'data')
storage = Storage(data_dir)

print('=== Привязка проектов к группам ===\n')

# Пример 1: TechnouprApp.Client → Auto line. Checklist
project1 = storage.get_project_by_name("TechnouprApp.Client")
if project1:
    project1.allowed_group_ids = [-4907156243]  # Auto line. Checklist
    storage.add_project(project1)
    print(f'✅ {project1.name} → Auto line. Checklist (ID: -4907156243)')
else:
    print('❌ Проект TechnouprApp.Client не найден')

# Пример 2: White Broker → Domyland platform
project2 = storage.get_project_by_name("White Broker")
if project2:
    project2.allowed_group_ids = [-935064553]  # Domyland platform
    storage.add_project(project2)
    print(f'✅ {project2.name} → Domyland platform (ID: -935064553)')
else:
    print('❌ Проект White Broker не найден')

print('\n=== Проверка результатов ===\n')
projects = storage.get_all_projects()
for p in projects:
    groups_str = ', '.join(str(g) for g in p.allowed_group_ids) if p.allowed_group_ids else 'ДЛЯ ВСЕХ ГРУПП'
    print(f'{p.name}: {groups_str}')

print('\n✅ Готово! Теперь проверьте команду /build в группах.')


