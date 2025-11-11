#!/usr/bin/env python3
"""
Простой скрипт для проверки структуры Xamarin проекта.
"""
import os
import sys
import glob
import xml.etree.ElementTree as ET


def check_xamarin_structure(repo_path: str):
    """
    Проверяет структуру Xamarin проекта.

    Args:
        repo_path: Путь к репозиторию
    """
    print(f"=== Проверка структуры Xamarin проекта ===")
    print(f"Директория: {repo_path}\n")

    if not os.path.exists(repo_path):
        print(f"❌ Директория не существует: {repo_path}")
        return

    print("✓ Директория существует\n")

    # Суффиксы платформенных проектов (как в коде бота)
    platform_suffixes = [
        '.Android.csproj',
        '.iOS.csproj',
        '.UWP.csproj',
        '.WinPhone.csproj',
        '.Droid.csproj'
    ]

    print(f"Ищем файлы с суффиксами: {', '.join(platform_suffixes)}\n")

    # Собираем все .csproj файлы
    all_csproj = []
    platform_files = []

    # Рекурсивно обходим все папки (как в коде бота)
    for root, dirs, files in os.walk(repo_path):
        # Пропускаем скрытые папки (начинающиеся с точки)
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith('.csproj'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_path)
                all_csproj.append((rel_path, file))

                # Проверяем, является ли файл платформенным
                for suffix in platform_suffixes:
                    if file.endswith(suffix):
                        platform_files.append((rel_path, suffix))
                        break

    if not all_csproj:
        print("❌ Не найдено ни одного .csproj файла\n")
        print(f"Проверьте, что в директории {repo_path} есть C# проекты")
        return

    print(f"✓ Найдено {len(all_csproj)} .csproj файлов:\n")

    # Проверяем каждый файл
    for rel_path, filename in all_csproj:
        print(f"📄 {rel_path}")

        # Определяем тип платформы
        platform = None
        filename_lower = filename.lower()

        if '.android.csproj' in filename_lower or '.droid.csproj' in filename_lower:
            platform = 'Android'
        elif '.ios.csproj' in filename_lower:
            platform = 'iOS'
        elif '.uwp.csproj' in filename_lower:
            platform = 'UWP'
        elif '.winphone.csproj' in filename_lower:
            platform = 'WinPhone'

        if platform:
            print(f"  ✓ Платформа: {platform}")

            # Читаем версию из файла
            full_path = os.path.join(repo_path, rel_path)
            try:
                tree = ET.parse(full_path)
                root = tree.getroot()

                # Проверяем namespace
                namespace = ''
                if root.tag.startswith('{'):
                    namespace = root.tag[root.tag.find('{'):root.tag.find('}') + 1]

                versions_found = []

                # Ищем PropertyGroup с учётом namespace
                property_group_paths = [
                    './/PropertyGroup',
                    f'.//{namespace}PropertyGroup' if namespace else None
                ]

                for path in property_group_paths:
                    if path is None:
                        continue

                    for prop_group in root.findall(path):
                        # Ищем ApplicationVersion
                        app_version = prop_group.find('ApplicationVersion')
                        if app_version is None and namespace:
                            app_version = prop_group.find(f'{namespace}ApplicationVersion')
                        if app_version is not None and app_version.text:
                            versions_found.append(('ApplicationVersion', app_version.text.strip()))

                        # Для Android ищем AndroidVersionCode
                        if platform == 'Android':
                            android_code = prop_group.find('AndroidVersionCode')
                            if android_code is None and namespace:
                                android_code = prop_group.find(f'{namespace}AndroidVersionCode')
                            if android_code is not None and android_code.text:
                                versions_found.append(('AndroidVersionCode', android_code.text.strip()))

                        # Для iOS ищем CFBundleVersion и CFBundleShortVersionString
                        if platform == 'iOS':
                            cf_version = prop_group.find('CFBundleVersion')
                            if cf_version is None and namespace:
                                cf_version = prop_group.find(f'{namespace}CFBundleVersion')
                            if cf_version is not None and cf_version.text:
                                versions_found.append(('CFBundleVersion', cf_version.text.strip()))

                            cf_short = prop_group.find('CFBundleShortVersionString')
                            if cf_short is None and namespace:
                                cf_short = prop_group.find(f'{namespace}CFBundleShortVersionString')
                            if cf_short is not None and cf_short.text:
                                versions_found.append(('CFBundleShortVersionString', cf_short.text.strip()))

                if versions_found:
                    print("  ✓ Найдены теги версий:")
                    for tag, value in versions_found:
                        print(f"    • <{tag}>{value}</{tag}>")
                else:
                    print("  ❌ Теги версий НЕ найдены!")
                    print(f"    Необходимо добавить в файл:")
                    if platform == 'Android':
                        print(f"      <ApplicationVersion>X.Y.Z</ApplicationVersion>")
                        print(f"      <AndroidVersionCode>N</AndroidVersionCode>")
                    else:
                        print(f"      <ApplicationVersion>X.Y.Z</ApplicationVersion>")
                        print(f"      <CFBundleVersion>X.Y.Z</CFBundleVersion>")

            except Exception as e:
                print(f"  ❌ Ошибка при чтении файла: {e}")
        else:
            print(f"  ℹ️  Не является платформенным файлом (не Android/iOS/UWP/WinPhone)")

        print()

    # Итоговая сводка
    print("="*60)
    print("ИТОГОВАЯ СВОДКА:")
    print("="*60)

    if platform_files:
        print(f"\n✓ Найдено {len(platform_files)} платформенных файлов:")
        for path, suffix in platform_files:
            print(f"  • {path} (суффикс: {suffix})")
    else:
        print("\n❌ Не найдено платформенных файлов!")
        print("\nВозможные причины:")
        print("  1. Файлы не называются *.Android.csproj или *.iOS.csproj")
        print("  2. Это не Xamarin проект")
        print("\nВсе найденные .csproj файлы:")
        for rel_path, filename in all_csproj:
            print(f"  • {rel_path}")
        print("\nДля Xamarin проектов файлы должны иметь названия типа:")
        print("  • MyApp.Android.csproj")
        print("  • MyApp.iOS.csproj")


def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("Использование: python check_xamarin_structure.py <путь_к_репозиторию>")
        print("\nПример: python check_xamarin_structure.py /home/olinyavod/projects/easybuild_bot/repos/fintech")
        sys.exit(1)

    repo_path = sys.argv[1]
    check_xamarin_structure(repo_path)


if __name__ == "__main__":
    main()
