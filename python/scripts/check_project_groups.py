#!/usr/bin/env python3
"""
Скрипт для привязки проектов к группам.
"""

from src.easybuild_bot.storage import Storage
import os

data_dir = os.path.join(os.getcwd(), 'data')
storage = Storage(data_dir)

print('=== Текущее состояние ===\n')
projects = storage.get_all_projects()
for p in projects:
    print(f'{p.name}: {p.allowed_group_ids if p.allowed_group_ids else "ДЛЯ ВСЕХ ГРУПП"}')

print('\n=== Доступные группы ===\n')
groups = storage.get_all_groups()
for i, g in enumerate(groups, 1):
    print(f'{i}. {g.group_name} (ID: {g.group_id})')

print('\n' + '='*60)
print('ИНСТРУКЦИЯ:')
print('='*60)
print('\nЧтобы привязать проект к группе, используйте команду:')
print('  /edit_project')
print('\nЗатем:')
print('  1. Выберите проект')
print('  2. Выберите поле "👥 Группы"')
print('  3. Выберите нужную группу из списка')
print('  4. Сохраните изменения')
print('\nИли выполните напрямую через Python:')
print('\nПример для TechnouprApp.Client → Auto line. Checklist:')
print('  project = storage.get_project_by_name("TechnouprApp.Client")')
print('  project.allowed_group_ids = [-4907156243]')
print('  storage.add_project(project)')
print('\nПример для White Broker → Domyland platform:')
print('  project = storage.get_project_by_name("White Broker")')
print('  project.allowed_group_ids = [-935064553]')
print('  storage.add_project(project)')
print('\n' + '='*60)


