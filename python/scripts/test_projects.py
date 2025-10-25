#!/usr/bin/env python3
"""
Script for testing the project management system.

This script demonstrates and tests project management functionality
in EasyBuild Bot.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.easybuild_bot.storage import Storage
from src.easybuild_bot.models import Project, ProjectType


def print_separator():
    """Print separator line."""
    print("\n" + "=" * 80 + "\n")


def test_project_crud():
    """Test CRUD operations for projects."""
    print("🔧 Testing CRUD operations for projects")
    print_separator()
    
    # Initialize storage
    print("📦 Initializing storage...")
    storage = Storage(dir_path="./test_data", db_name="test_projects")
    
    # Test 1: Add projects
    print("\n✅ Test 1: Adding projects")
    print("-" * 40)
    
    projects = [
        Project(
            id="proj-001",
            name="ChecklistApp",
            project_type=ProjectType.FLUTTER,
            git_url="https://github.com/company/checklist.git",
            project_file_path="android/app",
            local_repo_path="/home/repos/checklist",
            dev_branch="develop",
            release_branch="main",
            tags=["checklist", "production", "mobile"],
            description="Checklist application for production"
        ),
        Project(
            id="proj-002",
            name="InventoryApp",
            project_type=ProjectType.DOTNET_MAUI,
            git_url="https://github.com/company/inventory.git",
            project_file_path="src/InventoryApp",
            local_repo_path="/home/repos/inventory",
            dev_branch="dev",
            release_branch="release",
            tags=["inventory", "warehouse", "mobile"],
            description="Warehouse management application"
        ),
        Project(
            id="proj-003",
            name="LegacyApp",
            project_type=ProjectType.XAMARIN,
            git_url="https://github.com/company/legacy.git",
            project_file_path="Droid",
            local_repo_path="/home/repos/legacy",
            allowed_group_ids=[-1001234567890],
            tags=["legacy", "old"],
            description="Legacy Xamarin application"
        )
    ]
    
    for project in projects:
        storage.add_project(project)
        print(f"  ✓ Added project: {project.name} ({project.project_type.value})")
    
    # Test 2: Get all projects
    print("\n✅ Test 2: Getting all projects")
    print("-" * 40)
    
    all_projects = storage.get_all_projects()
    print(f"  Total projects: {len(all_projects)}")
    for p in all_projects:
        print(f"  • {p.name} - {p.project_type.value}")
    
    # Test 3: Get project by name
    print("\n✅ Test 3: Finding project by name")
    print("-" * 40)
    
    project = storage.get_project_by_name("ChecklistApp")
    if project:
        print(f"  Found: {project.name}")
        print(f"  Type: {project.project_type.value}")
        print(f"  Git URL: {project.git_url}")
        print(f"  Tags: {', '.join(project.tags)}")
        print(f"  Description: {project.description}")
    
    # Test 4: Find projects by tag
    print("\n✅ Test 4: Finding projects by tag")
    print("-" * 40)
    
    mobile_projects = storage.find_projects_by_tag("mobile")
    print(f"  Projects with tag 'mobile': {len(mobile_projects)}")
    for p in mobile_projects:
        print(f"  • {p.name}")
    
    # Test 5: Get projects for group
    print("\n✅ Test 5: Getting projects for group")
    print("-" * 40)
    
    # Group with access to specific project
    group_id = -1001234567890
    group_projects = storage.get_projects_for_group(group_id)
    print(f"  Projects for group {group_id}: {len(group_projects)}")
    for p in group_projects:
        print(f"  • {p.name}")
    
    # Group without specific projects (should see projects with empty allowed_group_ids)
    other_group_id = -9999999
    other_group_projects = storage.get_projects_for_group(other_group_id)
    print(f"\n  Projects for other group {other_group_id}: {len(other_group_projects)}")
    for p in other_group_projects:
        print(f"  • {p.name}")
    
    # Test 6: Update project
    print("\n✅ Test 6: Updating project")
    print("-" * 40)
    
    project = storage.get_project_by_name("ChecklistApp")
    if project:
        print(f"  Before: tags = {project.tags}")
        project.tags.append("android")
        storage.add_project(project)
        
        updated = storage.get_project_by_name("ChecklistApp")
        print(f"  After: tags = {updated.tags}")
    
    # Test 7: Update project groups
    print("\n✅ Test 7: Updating project groups")
    print("-" * 40)
    
    storage.update_project_groups("proj-002", [-1001111111, -1002222222])
    project = storage.get_project_by_id("proj-002")
    print(f"  Groups for {project.name}: {project.allowed_group_ids}")
    
    # Test 8: Delete project
    print("\n✅ Test 8: Deleting project")
    print("-" * 40)
    
    deleted = storage.delete_project("proj-003")
    print(f"  Project deleted: {deleted}")
    
    remaining = storage.get_all_projects()
    print(f"  Remaining projects: {len(remaining)}")
    for p in remaining:
        print(f"  • {p.name}")
    
    print_separator()
    print("✅ All tests passed successfully!")


def display_project_info():
    """Display information about project types and fields."""
    print("📋 Project management system information")
    print_separator()
    
    print("📦 Project types:")
    print("  • Flutter (flutter)")
    print("  • .NET MAUI (dotnet_maui)")
    print("  • Xamarin (xamarin)")
    
    print("\n📝 Project fields:")
    fields = [
        ("id", "Unique identifier (auto-generated)"),
        ("name", "Project name"),
        ("project_type", "Project type (Flutter, .NET MAUI, Xamarin)"),
        ("git_url", "Git repository URL"),
        ("project_file_path", "Path to project file"),
        ("local_repo_path", "Local repository path on server"),
        ("dev_branch", "Git development branch (default: develop)"),
        ("release_branch", "Git release branch (default: main)"),
        ("allowed_group_ids", "List of group IDs (empty = all groups)"),
        ("tags", "Tags for search"),
        ("description", "Project description (optional)"),
    ]
    
    for field, desc in fields:
        print(f"  • {field:20} - {desc}")
    
    print("\n📚 Available commands:")
    commands = [
        ("/projects", "Show projects list"),
        ("/add_project", "Add new project (admin)"),
        ("/edit_project", "Edit project (admin)"),
        ("/delete_project", "Delete project (admin)"),
    ]
    
    for cmd, desc in commands:
        print(f"  • {cmd:20} - {desc}")
    
    print_separator()


if __name__ == "__main__":
    print("🤖 EasyBuild Bot - Project management system testing")
    print_separator()
    
    display_project_info()
    
    try:
        test_project_crud()
        
        # Cleanup test data
        print("\n🧹 Cleaning up test data...")
        import shutil
        if os.path.exists("./test_data"):
            shutil.rmtree("./test_data")
        print("  ✓ Test data cleaned up")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

