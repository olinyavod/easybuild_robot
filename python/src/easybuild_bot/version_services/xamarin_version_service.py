"""
Version service for Xamarin projects.
"""

import os
import glob
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

        Args:
            project: Объект проекта

        Returns:
            Список относительных путей к найденным платформенным проектам
        """
        platform_projects = []
        base_path = project.local_repo_path

        # Паттерны для поиска платформенных проектов
        patterns = [
            '*.Android.csproj',
            '*.iOS.csproj',
            '*.UWP.csproj',
            '*.WinPhone.csproj',
            '*.Droid.csproj'
        ]

        logger.info(f"Поиск платформенных проектов Xamarin в {base_path}")

        for pattern in patterns:
            # Ищем в корне и во всех подкаталогах
            search_pattern = os.path.join(base_path, '**', pattern)
            found_files = glob.glob(search_pattern, recursive=True)

            for file_path in found_files:
                # Преобразуем в относительный путь
                rel_path = os.path.relpath(file_path, base_path)
                platform_projects.append(rel_path)
                logger.info(f"Найден платформенный проект: {rel_path}")

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
            return None

        try:
            tree = ET.parse(csproj_path)
            root = tree.getroot()

            # Определяем тип платформы по имени файла
            filename = os.path.basename(csproj_path)
            platform = self._get_platform_type(filename)

            # Ищем версию в PropertyGroup
            for prop_group in root.findall('.//PropertyGroup'):
                if platform == 'android':
                    # Для Android ищем ApplicationVersion
                    app_version_elem = prop_group.find('ApplicationVersion')
                    if app_version_elem is not None and app_version_elem.text:
                        return app_version_elem.text.strip()
                elif platform == 'ios':
                    # Для iOS ищем ApplicationVersion
                    app_version_elem = prop_group.find('ApplicationVersion')
                    if app_version_elem is not None and app_version_elem.text:
                        return app_version_elem.text.strip()
                    # Альтернативно CFBundleShortVersionString
                    cf_version_elem = prop_group.find('CFBundleShortVersionString')
                    if cf_version_elem is not None and cf_version_elem.text:
                        return cf_version_elem.text.strip()

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

            version_updated = False
            updated_tags = []

            # Обновляем теги версий в PropertyGroup
            for prop_group in root.findall('.//PropertyGroup'):
                if platform == 'android':
                    # Обновляем ApplicationVersion
                    app_version_elem = prop_group.find('ApplicationVersion')
                    if app_version_elem is not None:
                        app_version_elem.text = new_version
                        version_updated = True
                        if 'ApplicationVersion' not in updated_tags:
                            updated_tags.append('ApplicationVersion')

                    # Обновляем AndroidVersionCode (только числовую часть)
                    version_code_elem = prop_group.find('AndroidVersionCode')
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
                    if app_version_elem is not None:
                        app_version_elem.text = new_version
                        version_updated = True
                        if 'ApplicationVersion' not in updated_tags:
                            updated_tags.append('ApplicationVersion')

                    # Обновляем CFBundleShortVersionString
                    cf_version_elem = prop_group.find('CFBundleShortVersionString')
                    if cf_version_elem is not None:
                        cf_version_elem.text = new_version
                        version_updated = True
                        if 'CFBundleShortVersionString' not in updated_tags:
                            updated_tags.append('CFBundleShortVersionString')

                    # Обновляем CFBundleVersion (build number)
                    cf_build_elem = prop_group.find('CFBundleVersion')
                    if cf_build_elem is not None:
                        cf_build_elem.text = new_version
                        version_updated = True
                        if 'CFBundleVersion' not in updated_tags:
                            updated_tags.append('CFBundleVersion')

            if not version_updated:
                return False, f"Не найдены теги версии для платформы {platform} в файле {csproj_path}"

            # Записываем обновлённый XML
            tree.write(csproj_path, encoding='utf-8', xml_declaration=True)

            tags_str = ', '.join(updated_tags)
            return True, f"Версия обновлена на {new_version} (теги: {tags_str})"
        except Exception as e:
            return False, f"Ошибка при обновлении версии в {csproj_path}: {str(e)}"

    async def get_current_version(self, project: Project) -> Optional[str]:
        """
        Получает текущую версию из проекта Xamarin.
        Ищет версию только в платформенных файлах (*.Android.csproj, *.iOS.csproj).
        """
        # Ищем платформенные проекты
        platform_projects = self._find_platform_projects(project)

        if not platform_projects:
            logger.warning(f"Не найдено платформенных проектов (*.Android.csproj, *.iOS.csproj) в проекте {project.name}")
            return None

        logger.info(f"Найдено {len(platform_projects)} платформенных файлов: {', '.join(platform_projects)}")

        # Проверяем, есть ли Android и iOS проекты
        has_android = False
        has_ios = False
        found_version = None

        for platform_file in platform_projects:
            platform = self._get_platform_type(platform_file)
            if platform == 'android':
                has_android = True
            elif platform == 'ios':
                has_ios = True

            # Пытаемся получить версию из файла
            csproj_path = os.path.join(project.local_repo_path, platform_file)
            version = self._get_version_from_csproj(csproj_path)

            if version:
                logger.info(f"Версия {version} найдена в файле: {platform_file}")
                found_version = version
                break

        # Если не найдена версия ни в одном файле
        if not found_version:
            platforms_found = []
            if has_android:
                platforms_found.append('Android')
            if has_ios:
                platforms_found.append('iOS')

            if platforms_found:
                logger.warning(f"Найдены платформы: {', '.join(platforms_found)}, но версия не найдена")
            else:
                logger.warning(f"Не найдено проектов Android или iOS")

        return found_version

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
