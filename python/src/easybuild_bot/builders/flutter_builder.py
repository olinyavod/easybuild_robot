"""
Flutter project builder implementation.
"""

import os
import subprocess
import re
from typing import Optional
from .base import ProjectBuilder, BuildResult, BuildStep


class FlutterVersionManager:
    """Helper class for managing Flutter version in pubspec.yaml."""
    
    @staticmethod
    def update_version(pubspec_path: str, new_version: str) -> bool:
        """
        Update version in pubspec.yaml.
        
        Args:
            pubspec_path: Path to pubspec.yaml
            new_version: New version string (e.g., "1.2.3+4")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(pubspec_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace version line
            new_content = re.sub(
                r'^version:\s*.*$',
                f'version: {new_version}',
                content,
                flags=re.MULTILINE
            )
            
            with open(pubspec_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        except Exception:
            return False


class FlutterBuilder(ProjectBuilder):
    """Builder for Flutter projects."""
    
    def _get_commits_since_last_release(self) -> list[str]:
        """
        Get list of commits since last release tag.
        
        Returns:
            List of commit messages (short format)
        """
        try:
            # Get latest tag (if exists)
            tag_result = subprocess.run(
                ["git", "-C", self.project.local_repo_path, "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # If no tags exist, get all commits from dev branch
            if tag_result.returncode != 0:
                log_result = subprocess.run(
                    ["git", "-C", self.project.local_repo_path, "log", 
                     self.project.dev_branch, "--oneline", "-20"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                # Get commits since last tag
                last_tag = tag_result.stdout.strip()
                log_result = subprocess.run(
                    ["git", "-C", self.project.local_repo_path, "log", 
                     f"{last_tag}..{self.project.dev_branch}", "--oneline"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if log_result.returncode == 0:
                commits = log_result.stdout.strip().split('\n')
                # Filter out empty lines and limit to 10 commits
                commits = [c for c in commits if c.strip()][:10]
                return commits
            else:
                return []
                
        except Exception:
            return []
    
    async def prepare_environment(self) -> BuildResult:
        """Prepare Flutter environment."""
        await self.send_message("📦 Установка зависимостей Flutter...")
        
        try:
            # Run flutter pub get
            result = subprocess.run(
                ["flutter", "pub", "get"],
                cwd=self.project.local_repo_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode != 0:
                error_msg = f"Ошибка установки зависимостей:\n{result.stderr}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.DEPENDENCIES,
                    message="Failed to install dependencies",
                    error=error_msg
                )
            
            await self.send_message("✅ Зависимости успешно установлены")
            return BuildResult(
                success=True,
                step=BuildStep.DEPENDENCIES,
                message="Dependencies installed successfully"
            )
            
        except subprocess.TimeoutExpired:
            error_msg = "Превышено время ожидания установки зависимостей (5 минут)"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.DEPENDENCIES,
                message="Timeout",
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.DEPENDENCIES,
                message="Error",
                error=error_msg
            )
    
    async def build_debug(self) -> BuildResult:
        """Build debug APK."""
        await self.send_message("🔨 Сборка debug APK...")
        
        try:
            # Run flutter build apk --debug
            result = subprocess.run(
                ["flutter", "build", "apk", "--debug"],
                cwd=self.project.local_repo_path,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes
            )
            
            if result.returncode != 0:
                error_msg = f"Ошибка сборки:\n{result.stderr}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.BUILDING,
                    message="Build failed",
                    error=error_msg
                )
            
            # Find the APK file
            apk_path = os.path.join(
                self.project.local_repo_path,
                "build/app/outputs/flutter-apk/app-debug.apk"
            )
            
            if not os.path.exists(apk_path):
                error_msg = f"APK файл не найден: {apk_path}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.BUILDING,
                    message="APK not found",
                    error=error_msg
                )
            
            await self.send_message(f"✅ Debug APK успешно собран:\n📦 {apk_path}")
            return BuildResult(
                success=True,
                step=BuildStep.COMPLETED,
                message="Debug APK built successfully",
                artifact_path=apk_path
            )
            
        except subprocess.TimeoutExpired:
            error_msg = "Превышено время ожидания сборки (30 минут)"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.BUILDING,
                message="Timeout",
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.BUILDING,
                message="Error",
                error=error_msg
            )
    
    async def build_release(self) -> BuildResult:
        """Build release APK."""
        await self.send_message("🔨 Сборка release APK...")
        
        try:
            # Run flutter build apk --release
            result = subprocess.run(
                ["flutter", "build", "apk", "--release"],
                cwd=self.project.local_repo_path,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes
            )
            
            if result.returncode != 0:
                error_msg = f"Ошибка сборки:\n{result.stderr}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.BUILDING,
                    message="Build failed",
                    error=error_msg
                )
            
            # Find the APK file
            apk_path = os.path.join(
                self.project.local_repo_path,
                "build/app/outputs/flutter-apk/app-release.apk"
            )
            
            if not os.path.exists(apk_path):
                error_msg = f"APK файл не найден: {apk_path}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.BUILDING,
                    message="APK not found",
                    error=error_msg
                )
            
            await self.send_message(f"✅ Release APK успешно собран:\n📦 {apk_path}")
            return BuildResult(
                success=True,
                step=BuildStep.COMPLETED,
                message="Release APK built successfully",
                artifact_path=apk_path
            )
            
        except subprocess.TimeoutExpired:
            error_msg = "Превышено время ожидания сборки (30 минут)"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.BUILDING,
                message="Timeout",
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.BUILDING,
                message="Error",
                error=error_msg
            )
    
    async def get_version_info(self) -> Optional[str]:
        """Get version from pubspec.yaml."""
        try:
            pubspec_path = os.path.join(
                self.project.local_repo_path,
                self.project.project_file_path
            )
            
            if not os.path.exists(pubspec_path):
                return None
            
            with open(pubspec_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for version: line in pubspec.yaml
                match = re.search(r'^version:\s*([^\s]+)', content, re.MULTILINE)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    async def clean(self) -> BuildResult:
        """Clean Flutter build artifacts."""
        await self.send_message("🧹 Очистка build артефактов...")
        
        try:
            result = subprocess.run(
                ["flutter", "clean"],
                cwd=self.project.local_repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                error_msg = f"Ошибка очистки:\n{result.stderr}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.FAILED,
                    message="Clean failed",
                    error=error_msg
                )
            
            await self.send_message("✅ Артефакты успешно очищены")
            return BuildResult(
                success=True,
                step=BuildStep.COMPLETED,
                message="Clean successful"
            )
            
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.FAILED,
                message="Error",
                error=error_msg
            )
    
    async def supports_release_preparation(self) -> bool:
        """Flutter supports release preparation."""
        return True
    
    async def prepare_release(self, new_version: str) -> BuildResult:
        """
        Prepare release for Flutter:
        1. Merge dev branch into release branch
        2. Switch to release branch
        3. Update version in pubspec.yaml
        4. Commit changes
        """
        await self.send_message(
            f"🚀 Начинаем подготовку релиза версии {new_version}..."
        )
        
        try:
            # Step 1: Switch to release branch
            await self.send_message(
                f"🔀 Переключение на ветку релиза: {self.project.release_branch}..."
            )
            
            checkout_result = subprocess.run(
                ["git", "-C", self.project.local_repo_path, "checkout", self.project.release_branch],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if checkout_result.returncode != 0:
                error_msg = f"Не удалось переключиться на ветку {self.project.release_branch}:\n{checkout_result.stderr}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.PREPARING,
                    message="Failed to checkout release branch",
                    error=error_msg
                )
            
            # Step 2: Pull latest changes from release branch
            await self.send_message("⬇️ Получение последних изменений из ветки релиза...")
            
            pull_result = subprocess.run(
                ["git", "-C", self.project.local_repo_path, "pull", "origin", self.project.release_branch],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if pull_result.returncode != 0:
                # Warning, but continue
                await self.send_message(f"⚠️ Предупреждение при pull: {pull_result.stderr}")
            
            # Step 3: Merge dev branch into release branch
            await self.send_message(
                f"🔄 Мердж изменений из {self.project.dev_branch} в {self.project.release_branch}..."
            )
            
            merge_result = subprocess.run(
                ["git", "-C", self.project.local_repo_path, "merge", self.project.dev_branch, "-m", f"Merge {self.project.dev_branch} for release {new_version}"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if merge_result.returncode != 0:
                error_msg = f"Ошибка при мердже:\n{merge_result.stderr}"
                await self.send_message(f"❌ {error_msg}")
                
                # Try to abort merge
                subprocess.run(
                    ["git", "-C", self.project.local_repo_path, "merge", "--abort"],
                    capture_output=True
                )
                
                return BuildResult(
                    success=False,
                    step=BuildStep.PREPARING,
                    message="Failed to merge branches",
                    error=error_msg
                )
            
            await self.send_message("✅ Ветки успешно смерджены")
            
            # Step 4: Update version in pubspec.yaml
            await self.send_message(f"📝 Обновление версии в pubspec.yaml на {new_version}...")
            
            pubspec_path = os.path.join(
                self.project.local_repo_path,
                self.project.project_file_path
            )
            
            if not FlutterVersionManager.update_version(pubspec_path, new_version):
                error_msg = "Не удалось обновить версию в pubspec.yaml"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.PREPARING,
                    message="Failed to update version",
                    error=error_msg
                )
            
            await self.send_message(f"✅ Версия обновлена на {new_version}")
            
            # Step 5: Commit changes
            await self.send_message("💾 Коммит изменений...")
            
            # Add pubspec.yaml
            add_result = subprocess.run(
                ["git", "-C", self.project.local_repo_path, "add", self.project.project_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if add_result.returncode != 0:
                error_msg = f"Ошибка при добавлении файла: {add_result.stderr}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.PREPARING,
                    message="Failed to add file",
                    error=error_msg
                )
            
            # Commit
            commit_result = subprocess.run(
                ["git", "-C", self.project.local_repo_path, "commit", "-m", f"Bump version to {new_version}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if commit_result.returncode != 0:
                error_msg = f"Ошибка при коммите: {commit_result.stderr}"
                await self.send_message(f"⚠️ {error_msg}")
                # This might be OK if there are no changes
            else:
                await self.send_message("✅ Изменения закоммичены")
            
            # Step 6: Get commits since last release
            commits = self._get_commits_since_last_release()
            
            # Step 7: Show summary
            summary = f"🎉 Релиз v{new_version} подготовлен!"
            
            if commits:
                summary += "\n\n📝 Список изменений:"
                for commit in commits:
                    # Remove hash and clean up message
                    commit_msg = ' '.join(commit.split()[1:])
                    summary += f"\n• {commit_msg}"
            
            summary += f"\n\n⚠️ Не забудьте сделать push:\n`git push origin {self.project.release_branch}`"
            
            await self.send_message(summary)
            
            return BuildResult(
                success=True,
                step=BuildStep.COMPLETED,
                message=f"Release {new_version} prepared successfully"
            )
            
        except subprocess.TimeoutExpired:
            error_msg = "Превышено время ожидания операции"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.PREPARING,
                message="Timeout",
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            await self.send_message(f"❌ {error_msg}")
            return BuildResult(
                success=False,
                step=BuildStep.PREPARING,
                message="Error",
                error=error_msg
            )


