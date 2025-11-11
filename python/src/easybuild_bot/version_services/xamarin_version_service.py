"""
Version service for Xamarin projects.
"""

import os
import logging
import xml.etree.ElementTree as ET
from typing import Optional, Tuple, List
from .base import VersionService
from ..models import Project

logger = logging.getLogger(__name__)


class XamarinVersionService(VersionService):
    """Version service for Xamarin projects (.csproj files)."""

    def _find_platform_projects(self, project: Project) -> List[str]:
        """
        Находит все платформенные проекты Xamarin (.Android.csproj, .iOS.csproj и т.д.).
        Использует os.walk() для рекурсивного поиска в подпапках.

        Args:
            project: Объект проекта

        Returns:
            Список относительных путей к найденным платформенным проектам
        """
        platform_projects = []
        base_path = project.local_repo_path

        # Суффиксы для поиска платформенных проектов
        platform_suffixes = [
            '.Android.csproj',
            '.iOS.csproj',
            '.UWP.csproj',
            '.WinPhone.csproj',
            '.Droid.csproj'
        ]

        logger.info(f"Поиск платформенных проектов Xamarin в {base_path}")
        logger.info(f"Ищем файлы с суффиксами: {', '.join(platform_suffixes)}")

        # Рекурсивно обходим все папки
        for root, dirs, files in os.walk(base_path):
            # Пропускаем скрытые папки (начинающиеся с точки)
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                # Проверяем, заканчивается ли файл на один из суффиксов
                for suffix in platform_suffixes:
                    if file.endswith(suffix):
                        # Полный путь к файлу
                        full_path = os.path.join(root, file)
                        # Относительный путь от base_path
                        rel_path = os.path.relpath(full_path, base_path)
                        platform_projects.append(rel_path)
                        logger.info(f"✓ Найден платформенный проект: {rel_path}")
                        break  # Файл уже найден, не проверяем другие суффиксы

        if not platform_projects:
            logger.warning(f"✗ Не найдено ни одного платформенного проекта")
            logger.warning(f"  Проверяли директорию: {base_path}")
            logger.warning(f"  Искали файлы: {', '.join(platform_suffixes)}")
        else:
            logger.info(f"✓ Всего найдено платформенных проектов: {len(platform_projects)}")

        return platform_projects

    def _get_platform_type(self, csproj_filename: str) -> Optional[str]:
        """
        Определяет тип платформы по имени файла.

        Args:
            csproj_filename: Имя файла .csproj

        Returns:
            'android', 'ios' или None для других платформ
        """
        filename_lower = csproj_filename.lower()
        if '.android.csproj' in filename_lower or '.droid.csproj' in filename_lower:
            return 'android'
        elif '.ios.csproj' in filename_lower:
            return 'ios'
        return None

    def _get_version_from_csproj(self, csproj_path: str) -> Optional[str]:
        """
        Получает версию из указанного .csproj файла платформы.
        Для Android ищет ApplicationVersion и AndroidVersionCode.
        Для iOS ищет ApplicationVersion и CFBundleVersion.

        Args:
            csproj_path: Полный путь к .csproj файлу

        Returns:
            Строка версии или None, если версия не найдена
        """
        if not os.path.exists(csproj_path):
            logger.warning(f"Файл не существует: {csproj_path}")
            return None

        try:
            logger.info(f"Читаем версию из файла: {csproj_path}")
            tree = ET.parse(csproj_path)
            root = tree.getroot()

            # Определяем тип платформы по имени файла
            filename = os.path.basename(csproj_path)
            platform = self._get_platform_type(filename)
            logger.info(f"Тип платформы для {filename}: {platform}")

            # Проверяем namespace в корневом элементе
            namespace = ''
            if root.tag.startswith('{'):
                # Извлекаем namespace из тега
                namespace = root.tag[root.tag.find('{'):root.tag.find('}') + 1]
                logger.debug(f"Обнаружен XML namespace: {namespace}")

            # Ищем версию в PropertyGroup
            prop_groups_count = 0
            # Ищем с учётом namespace и без него
            property_group_paths = [
                './/PropertyGroup',  # Без namespace
                f'.//{namespace}PropertyGroup' if namespace else None  # С namespace
            ]

            for path in property_group_paths:
                if path is None:
                    continue

                for prop_group in root.findall(path):
                    prop_groups_count += 1
                    logger.debug(f"Проверяем PropertyGroup #{prop_groups_count}")

                    if platform == 'android':
                        # Для Android ищем ApplicationVersion
                        # Пробуем с namespace и без
                        app_version_elem = prop_group.find('ApplicationVersion')
                        if app_version_elem is None and namespace:
                            app_version_elem = prop_group.find(f'{namespace}ApplicationVersion')

                        if app_version_elem is not None and app_version_elem.text:
                            version = app_version_elem.text.strip()
                            logger.info(f"✓ Найдена версия в ApplicationVersion: {version}")
                            return version
                        else:
                            logger.debug("  ApplicationVersion не найден в этой группе")
                    elif platform == 'ios':
                        # Для iOS ищем ApplicationVersion
                        app_version_elem = prop_group.find('ApplicationVersion')
                        if app_version_elem is None and namespace:
                            app_version_elem = prop_group.find(f'{namespace}ApplicationVersion')

                        if app_version_elem is not None and app_version_elem.text:
                            version = app_version_elem.text.strip()
                            logger.info(f"✓ Найдена версия в ApplicationVersion: {version}")
                            return version

                        # Альтернативно CFBundleShortVersionString
                        cf_version_elem = prop_group.find('CFBundleShortVersionString')
                        if cf_version_elem is None and namespace:
                            cf_version_elem = prop_group.find(f'{namespace}CFBundleShortVersionString')

                        if cf_version_elem is not None and cf_version_elem.text:
                            version = cf_version_elem.text.strip()
                            logger.info(f"✓ Найдена версия в CFBundleShortVersionString: {version}")
                            return version
                        logger.debug("  ApplicationVersion и CFBundleShortVersionString не найдены в этой группе")
                    else:
                        logger.warning(f"  Неопределённый тип платформы: {platform}")

            logger.warning(f"✗ Версия не найдена ни в одной из {prop_groups_count} PropertyGroup в файле {filename}")
            logger.warning(f"  Убедитесь, что в файле есть тег <ApplicationVersion>X.Y.Z</ApplicationVersion>")
            return None
        except Exception as e:
            logger.error(f"Ошибка при чтении версии из {csproj_path}: {str(e)}", exc_info=True)
            return None

    def _update_version_in_csproj(self, csproj_path: str, new_version: str) -> Tuple[bool, str]:
        """
        Обновляет версию в указанном .csproj файле платформы.
        Для Android обновляет ApplicationVersion и AndroidVersionCode.
        Для iOS обновляет ApplicationVersion и CFBundleVersion.

        Args:
            csproj_path: Полный путь к .csproj файлу
            new_version: Новая версия

        Returns:
            Кортеж (успешно, сообщение)
        """
        if not os.path.exists(csproj_path):
            return False, f"Файл проекта не найден: {csproj_path}"

        try:
            tree = ET.parse(csproj_path)
            root = tree.getroot()

            # Определяем тип платформы по имени файла
            filename = os.path.basename(csproj_path)
            platform = self._get_platform_type(filename)

            if platform not in ['android', 'ios']:
                return False, f"Файл {filename} не является Android или iOS проектом"

            # Проверяем namespace в корневом элементе
            namespace = ''
            if root.tag.startswith('{'):
                # Извлекаем namespace из тега
                namespace = root.tag[root.tag.find('{'):root.tag.find('}') + 1]
                logger.debug(f"Обнаружен XML namespace при обновлении: {namespace}")

            version_updated = False
            updated_tags = []

            # Ищем PropertyGroup с учётом namespace и без него
            property_group_paths = [
                './/PropertyGroup',  # Без namespace
                f'.//{namespace}PropertyGroup' if namespace else None  # С namespace
            ]

            for path in property_group_paths:
                if path is None:
                    continue

                for prop_group in root.findall(path):
                    if platform == 'android':
                        # Обновляем ApplicationVersion
                        app_version_elem = prop_group.find('ApplicationVersion')
                        if app_version_elem is None and namespace:
                            app_version_elem = prop_group.find(f'{namespace}ApplicationVersion')

                        if app_version_elem is not None:
                            app_version_elem.text = new_version
                            version_updated = True
                            if 'ApplicationVersion' not in updated_tags:
                                updated_tags.append('ApplicationVersion')

                        # Обновляем AndroidVersionCode (только числовую часть)
                        version_code_elem = prop_group.find('AndroidVersionCode')
                        if version_code_elem is None and namespace:
                            version_code_elem = prop_group.find(f'{namespace}AndroidVersionCode')

                        if version_code_elem is not None:
                            # Генерируем версионный код из версии (например, 1.2.3 -> 10203)
                            try:
                                parts = new_version.split('.')
                                if len(parts) >= 3:
                                    version_code = int(parts[0]) * 10000 + int(parts[1]) * 100 + int(parts[2])
                                    version_code_elem.text = str(version_code)
                                    version_updated = True
                                    if 'AndroidVersionCode' not in updated_tags:
                                        updated_tags.append('AndroidVersionCode')
                            except (ValueError, IndexError):
                                logger.warning(f"Не удалось сгенерировать AndroidVersionCode из версии {new_version}")

                    elif platform == 'ios':
                        # Обновляем ApplicationVersion
                        app_version_elem = prop_group.find('ApplicationVersion')
                        if app_version_elem is None and namespace:
                            app_version_elem = prop_group.find(f'{namespace}ApplicationVersion')

                        if app_version_elem is not None:
                            app_version_elem.text = new_version
                            version_updated = True
                            if 'ApplicationVersion' not in updated_tags:
                                updated_tags.append('ApplicationVersion')

                        # Обновляем CFBundleShortVersionString
                        cf_version_elem = prop_group.find('CFBundleShortVersionString')
                        if cf_version_elem is None and namespace:
                            cf_version_elem = prop_group.find(f'{namespace}CFBundleShortVersionString')

                        if cf_version_elem is not None:
                            cf_version_elem.text = new_version
                            version_updated = True
                            if 'CFBundleShortVersionString' not in updated_tags:
                                updated_tags.append('CFBundleShortVersionString')

                        # Обновляем CFBundleVersion (build number)
                        cf_build_elem = prop_group.find('CFBundleVersion')
                        if cf_build_elem is None and namespace:
                            cf_build_elem = prop_group.find(f'{namespace}CFBundleVersion')

                        if cf_build_elem is not None:
                            cf_build_elem.text = new_version
                            version_updated = True
                            if 'CFBundleVersion' not in updated_tags:
                                updated_tags.append('CFBundleVersion')

            if not version_updated:
                return False, f"Не найдены теги версии для платформы {platform} в файле {csproj_path}"

            # Сохраняем изменения напрямую в текст файла, чтобы сохранить форматирование
            import re

            # Читаем содержимое файла
            with open(csproj_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # Обновляем теги в тексте с помощью регулярных выражений
            if platform == 'android':
                # Обновляем ApplicationVersion
                content = re.sub(
                    r'(<ApplicationVersion>)[^<]+(</ApplicationVersion>)',
                    rf'\g<1>{new_version}\g<2>',
                    content
                )
                # Обновляем AndroidVersionCode
                parts = new_version.split('.')
                if len(parts) >= 3:
                    version_code = int(parts[0]) * 10000 + int(parts[1]) * 100 + int(parts[2])
                    content = re.sub(
                        r'(<AndroidVersionCode>)[^<]+(</AndroidVersionCode>)',
                        rf'\g<1>{version_code}\g<2>',
                        content
                    )
            elif platform == 'ios':
                # Обновляем ApplicationVersion
                content = re.sub(
                    r'(<ApplicationVersion>)[^<]+(</ApplicationVersion>)',
                    rf'\g<1>{new_version}\g<2>',
                    content
                )
                # Обновляем CFBundleVersion
                content = re.sub(
                    r'(<CFBundleVersion>)[^<]+(</CFBundleVersion>)',
                    rf'\g<1>{new_version}\g<2>',
                    content
                )
                # Обновляем CFBundleShortVersionString
                content = re.sub(
                    r'(<CFBundleShortVersionString>)[^<]+(</CFBundleShortVersionString>)',
                    rf'\g<1>{new_version}\g<2>',
                    content
                )

            # Записываем обратно с сохранением BOM
            with open(csproj_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)

            tags_str = ', '.join(updated_tags)
            return True, f"Версия обновлена на {new_version} (теги: {tags_str})"
        except Exception as e:
            return False, f"Ошибка при обновлении версии в {csproj_path}: {str(e)}"

    async def get_current_version(self, project: Project) -> Optional[str]:
        """
        Получает текущую версию из проекта Xamarin.
        Ищет версию только в платформенных файлах (*.Android.csproj, *.iOS.csproj).
        """
        logger.info(f"=== Определение версии для проекта Xamarin: {project.name} ===")
        logger.info(f"Локальный путь репозитория: {project.local_repo_path}")

        # Проверяем, существует ли локальный репозиторий
        if not os.path.exists(project.local_repo_path):
            logger.error(f"Локальный репозиторий не существует: {project.local_repo_path}")
            return None

        # Ищем платформенные проекты
        platform_projects = self._find_platform_projects(project)

        if not platform_projects:
            logger.warning(f"✗ Не найдено платформенных проектов (*.Android.csproj, *.iOS.csproj) в проекте {project.name}")
            logger.warning(f"  Искали в директории: {project.local_repo_path}")

            # Выведем список всех .csproj файлов для диагностики
            all_csproj = []
            for root, dirs, files in os.walk(project.local_repo_path):
                for file in files:
                    if file.endswith('.csproj'):
                        rel_path = os.path.relpath(os.path.join(root, file), project.local_repo_path)
                        all_csproj.append(rel_path)

            if all_csproj:
                logger.warning(f"  Найдены .csproj файлы (но не платформенные):")
                for csproj in all_csproj:
                    logger.warning(f"    • {csproj}")
                logger.warning(f"  Убедитесь, что файлы называются *.Android.csproj или *.iOS.csproj")
            else:
                logger.warning(f"  В директории вообще не найдено .csproj файлов")

            return None

        logger.info(f"✓ Найдено {len(platform_projects)} платформенных файлов:")
        for pf in platform_projects:
            logger.info(f"  • {pf}")

        # Проверяем, есть ли Android и iOS проекты
        has_android = False
        has_ios = False
        found_version = None
        checked_files = []

        for platform_file in platform_projects:
            platform = self._get_platform_type(platform_file)
            checked_files.append((platform_file, platform))

            if platform == 'android':
                has_android = True
            elif platform == 'ios':
                has_ios = True

            # Пытаемся получить версию из файла
            csproj_path = os.path.join(project.local_repo_path, platform_file)
            version = self._get_version_from_csproj(csproj_path)

            if version:
                logger.info(f"✓ Версия {version} найдена в файле: {platform_file}")
                found_version = version
                break

        # Если не найдена версия ни в одном файле
        if not found_version:
            platforms_found = []
            if has_android:
                platforms_found.append('Android')
            if has_ios:
                platforms_found.append('iOS')

            logger.warning(f"✗ Версия не найдена ни в одном из проверенных файлов:")
            for file, platform in checked_files:
                logger.warning(f"  • {file} (платформа: {platform or 'неизвестно'})")

            if platforms_found:
                logger.warning(f"Найдены платформы: {', '.join(platforms_found)}, но версия не найдена в них")
                logger.warning(f"Проверьте, что в файлах присутствуют теги:")
                logger.warning(f"  - Для Android: <ApplicationVersion>X.Y.Z</ApplicationVersion>")
                logger.warning(f"  - Для iOS: <ApplicationVersion>X.Y.Z</ApplicationVersion> или <CFBundleShortVersionString>X.Y.Z</CFBundleShortVersionString>")
            else:
                logger.warning(f"Не найдено проектов Android или iOS среди файлов")
        else:
            logger.info(f"=== Версия успешно определена: {found_version} ===")

        return found_version

    def get_version_diagnostic_info(self, project: Project) -> str:
        """
        Возвращает детальную диагностическую информацию о том, почему не удалось определить версию.
        Используется для формирования информативного сообщения пользователю.

        Args:
            project: Объект проекта

        Returns:
            Строка с диагностической информацией
        """
        diagnostic_lines = []

        # Проверяем существование репозитория
        if not os.path.exists(project.local_repo_path):
            diagnostic_lines.append(f"🔴 **Репозиторий не клонирован**")
            diagnostic_lines.append(f"   Путь: `{project.local_repo_path}`")
            diagnostic_lines.append(f"   💡 Запустите первую сборку, чтобы клонировать репозиторий")
            return "\n".join(diagnostic_lines)

        diagnostic_lines.append(f"✅ Репозиторий существует: `{project.local_repo_path}`")

        # Ищем платформенные проекты
        platform_projects = self._find_platform_projects(project)

        if not platform_projects:
            diagnostic_lines.append(f"\n🔴 **Не найдено платформенных файлов**")

            # Ищем все .csproj файлы
            all_csproj = []
            for root, dirs, files in os.walk(project.local_repo_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.endswith('.csproj'):
                        rel_path = os.path.relpath(os.path.join(root, file), project.local_repo_path)
                        all_csproj.append(rel_path)

            if all_csproj:
                diagnostic_lines.append(f"\n📄 Найдены .csproj файлы, но они не являются платформенными:")
                for csproj in all_csproj[:5]:  # Показываем первые 5
                    diagnostic_lines.append(f"   • `{csproj}`")
                if len(all_csproj) > 5:
                    diagnostic_lines.append(f"   • ... и ещё {len(all_csproj) - 5} файл(ов)")

                diagnostic_lines.append(f"\n💡 **Решение:**")
                diagnostic_lines.append(f"   Переименуйте файлы в:")
                diagnostic_lines.append(f"   • `*.Android.csproj` для Android")
                diagnostic_lines.append(f"   • `*.iOS.csproj` для iOS")
            else:
                diagnostic_lines.append(f"\n📄 В репозитории вообще нет .csproj файлов")
                diagnostic_lines.append(f"\n💡 Убедитесь, что это действительно Xamarin проект")

            return "\n".join(diagnostic_lines)

        # Есть платформенные файлы, проверяем версии
        diagnostic_lines.append(f"\n✅ Найдено {len(platform_projects)} платформенных файлов:")

        has_android = False
        has_ios = False
        files_without_version = []

        for platform_file in platform_projects:
            platform = self._get_platform_type(platform_file)
            if platform == 'android':
                has_android = True
            elif platform == 'ios':
                has_ios = True

            platform_name = platform.upper() if platform else "???"
            diagnostic_lines.append(f"   • `{platform_file}` ({platform_name})")

            # Проверяем наличие версии
            csproj_path = os.path.join(project.local_repo_path, platform_file)
            version = self._get_version_from_csproj(csproj_path)

            if not version:
                files_without_version.append((platform_file, platform))

        if files_without_version:
            diagnostic_lines.append(f"\n🔴 **Версия не найдена в файлах:**")
            for file, platform in files_without_version:
                diagnostic_lines.append(f"   • `{file}`")

            diagnostic_lines.append(f"\n💡 **Решение:**")
            diagnostic_lines.append(f"   Добавьте теги версий в PropertyGroup:")

            if has_android:
                diagnostic_lines.append(f"\n   **Для Android:**")
                diagnostic_lines.append(f"   ```xml")
                diagnostic_lines.append(f"   <PropertyGroup>")
                diagnostic_lines.append(f"     <ApplicationVersion>1.0.0</ApplicationVersion>")
                diagnostic_lines.append(f"     <AndroidVersionCode>10000</AndroidVersionCode>")
                diagnostic_lines.append(f"   </PropertyGroup>")
                diagnostic_lines.append(f"   ```")

            if has_ios:
                diagnostic_lines.append(f"\n   **Для iOS:**")
                diagnostic_lines.append(f"   ```xml")
                diagnostic_lines.append(f"   <PropertyGroup>")
                diagnostic_lines.append(f"     <ApplicationVersion>1.0.0</ApplicationVersion>")
                diagnostic_lines.append(f"     <CFBundleVersion>1.0.0</CFBundleVersion>")
                diagnostic_lines.append(f"   </PropertyGroup>")
                diagnostic_lines.append(f"   ```")

        return "\n".join(diagnostic_lines)

    async def update_version(self, project: Project, new_version: str) -> Tuple[bool, str]:
        """
        Обновляет версию в платформенных файлах проекта Xamarin.
        Обрабатывает только *.Android.csproj и *.iOS.csproj файлы.
        """
        updated_files = []
        failed_files = []
        messages = []

        # Находим платформенные проекты
        platform_projects = self._find_platform_projects(project)

        if not platform_projects:
            return False, (
                f"Не найдено платформенных проектов (*.Android.csproj или *.iOS.csproj) в проекте.\n"
                f"Убедитесь, что в проекте есть файлы:\n"
                f"  - Для Android: *.Android.csproj или *.Droid.csproj\n"
                f"  - Для iOS: *.iOS.csproj"
            )

        logger.info(f"Найдено {len(platform_projects)} платформенных файлов для обновления версии")

        # Проверяем, какие платформы найдены
        has_android = False
        has_ios = False
        android_files = []
        ios_files = []

        for platform_file in platform_projects:
            platform = self._get_platform_type(platform_file)
            if platform == 'android':
                has_android = True
                android_files.append(platform_file)
            elif platform == 'ios':
                has_ios = True
                ios_files.append(platform_file)

        # Обновляем версию в каждом файле
        for platform_file in platform_projects:
            platform = self._get_platform_type(platform_file)

            # Пропускаем файлы, которые не являются Android или iOS
            if platform not in ['android', 'ios']:
                logger.info(f"Пропускаем файл {platform_file} (не Android и не iOS)")
                continue

            platform_path = os.path.join(project.local_repo_path, platform_file)
            success, message = self._update_version_in_csproj(platform_path, new_version)

            if success:
                updated_files.append(platform_file)
                logger.info(f"Версия обновлена в платформенном файле: {platform_file}")
            else:
                failed_files.append(platform_file)
                messages.append(f"{platform_file}: {message}")
                logger.error(f"Не удалось обновить версию в {platform_file}: {message}")

        # Формируем итоговое сообщение
        if updated_files and not failed_files:
            files_list = '\n  • '.join(updated_files)
            platform_info = []
            if has_android:
                platform_info.append(f"Android ({len(android_files)})")
            if has_ios:
                platform_info.append(f"iOS ({len(ios_files)})")

            return True, (
                f"✅ Версия успешно обновлена на {new_version}\n\n"
                f"Платформы: {', '.join(platform_info)}\n\n"
                f"Обновлённые файлы:\n  • {files_list}"
            )
        elif updated_files and failed_files:
            success_list = '\n  • '.join(updated_files)
            failed_list = '\n  • '.join(messages)
            return True, (
                f"⚠️ Версия частично обновлена на {new_version}\n\n"
                f"Успешно:\n  • {success_list}\n\n"
                f"Ошибки:\n  • {failed_list}"
            )
        else:
            missing_platforms = []
            if not has_android:
                missing_platforms.append("Android (*.Android.csproj)")
            if not has_ios:
                missing_platforms.append("iOS (*.iOS.csproj)")

            error_msg = f"❌ Не удалось обновить версию ни в одном файле\n\n"

            if missing_platforms:
                error_msg += f"Не найдены платформы:\n  • " + '\n  • '.join(missing_platforms) + "\n\n"

            if failed_files:
                error_list = '\n  • '.join(messages)
                error_msg += f"Ошибки:\n  • {error_list}\n\n"

            error_msg += (
                f"Убедитесь, что в платформенных файлах есть теги:\n"
                f"  - Для Android: <ApplicationVersion>X.Y.Z</ApplicationVersion> и <AndroidVersionCode>N</AndroidVersionCode>\n"
                f"  - Для iOS: <ApplicationVersion>X.Y.Z</ApplicationVersion> и <CFBundleVersion>X.Y.Z</CFBundleVersion>"
            )

            return False, error_msg
