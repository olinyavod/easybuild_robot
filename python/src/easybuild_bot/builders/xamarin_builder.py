"""
Xamarin project builder implementation.
"""

import os
import subprocess
import re
from typing import Optional
from .base import ProjectBuilder, BuildResult, BuildStep


class XamarinBuilder(ProjectBuilder):
    """Builder for Xamarin projects."""
    
    async def prepare_environment(self) -> BuildResult:
        """Prepare Xamarin environment."""
        await self.send_message("📦 Восстановление NuGet пакетов...")
        
        try:
            # Run nuget restore or msbuild /t:Restore
            result = subprocess.run(
                ["msbuild", "/t:Restore"],
                cwd=self.project.local_repo_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            if result.returncode != 0:
                error_msg = f"Ошибка восстановления пакетов:\n{result.stderr}"
                await self.send_message(f"❌ {error_msg}")
                return BuildResult(
                    success=False,
                    step=BuildStep.DEPENDENCIES,
                    message="Failed to restore packages",
                    error=error_msg
                )
            
            await self.send_message("✅ Пакеты успешно восстановлены")
            return BuildResult(
                success=True,
                step=BuildStep.DEPENDENCIES,
                message="Packages restored successfully"
            )
            
        except subprocess.TimeoutExpired:
            error_msg = "Превышено время ожидания восстановления пакетов (10 минут)"
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
        """Build debug APK for Android."""
        await self.send_message("🔨 Сборка debug APK для Android...")
        
        try:
            project_file = os.path.join(
                self.project.local_repo_path,
                self.project.project_file_path
            )
            
            # Run msbuild for Android Debug
            result = subprocess.run(
                [
                    "msbuild", project_file,
                    "/p:Configuration=Debug",
                    "/p:Platform=AnyCPU",
                    "/t:PackageForAndroid"
                ],
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
            
            # Try to find the APK file
            # Usually in bin/Debug/
            bin_dir = os.path.join(
                self.project.local_repo_path,
                os.path.dirname(self.project.project_file_path),
                "bin/Debug"
            )
            
            apk_path = None
            if os.path.exists(bin_dir):
                for file in os.listdir(bin_dir):
                    if file.endswith(".apk"):
                        apk_path = os.path.join(bin_dir, file)
                        break
            
            if not apk_path or not os.path.exists(apk_path):
                error_msg = f"APK файл не найден в {bin_dir}"
                await self.send_message(f"⚠️ {error_msg}")
            else:
                await self.send_message(f"✅ Debug APK успешно собран:\n📦 {apk_path}")
            
            return BuildResult(
                success=True,
                step=BuildStep.COMPLETED,
                message="Debug build completed",
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
        """Build release APK for Android."""
        await self.send_message("🔨 Сборка release APK для Android...")
        
        try:
            project_file = os.path.join(
                self.project.local_repo_path,
                self.project.project_file_path
            )
            
            # Run msbuild for Android Release
            result = subprocess.run(
                [
                    "msbuild", project_file,
                    "/p:Configuration=Release",
                    "/p:Platform=AnyCPU",
                    "/t:PackageForAndroid"
                ],
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
            
            # Try to find the APK file
            bin_dir = os.path.join(
                self.project.local_repo_path,
                os.path.dirname(self.project.project_file_path),
                "bin/Release"
            )
            
            apk_path = None
            if os.path.exists(bin_dir):
                for file in os.listdir(bin_dir):
                    if file.endswith(".apk"):
                        apk_path = os.path.join(bin_dir, file)
                        break
            
            if not apk_path or not os.path.exists(apk_path):
                error_msg = f"APK файл не найден в {bin_dir}"
                await self.send_message(f"⚠️ {error_msg}")
            else:
                await self.send_message(f"✅ Release APK успешно собран:\n📦 {apk_path}")
            
            return BuildResult(
                success=True,
                step=BuildStep.COMPLETED,
                message="Release build completed",
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
        """Get version from AssemblyInfo or .csproj file."""
        try:
            project_file = os.path.join(
                self.project.local_repo_path,
                self.project.project_file_path
            )
            
            if not os.path.exists(project_file):
                return None
            
            with open(project_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for <Version> or <ApplicationVersion> tag
                match = re.search(r'<Version>([^<]+)</Version>', content)
                if not match:
                    match = re.search(r'<ApplicationVersion>([^<]+)</ApplicationVersion>', content)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    async def clean(self) -> BuildResult:
        """Clean Xamarin build artifacts."""
        await self.send_message("🧹 Очистка build артефактов...")
        
        try:
            result = subprocess.run(
                ["msbuild", "/t:Clean"],
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




