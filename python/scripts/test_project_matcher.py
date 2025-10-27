#!/usr/bin/env python3
"""
Test script for ProjectMatcher - semantic project search by tags.

Usage:
    cd /home/olinyavod/projects/easybuild_bot/python
    source .venv/bin/activate
    python scripts/test_project_matcher.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.easybuild_bot.storage import Storage
from src.easybuild_bot.project_matcher import ProjectMatcher
from src.easybuild_bot.models import Project, ProjectType

def main():
    print("=" * 80)
    print("PROJECT MATCHER TEST")
    print("=" * 80)
    print()
    
    # Initialize storage
    print("📦 Initializing storage...")
    storage = Storage()
    
    # Get all projects
    projects = storage.get_all_projects()
    
    if not projects:
        print("❌ No projects found in database!")
        print()
        print("Please add projects first using /add_project command")
        return
    
    print(f"✅ Found {len(projects)} project(s)")
    print()
    
    # Show projects with tags
    print("📋 Projects with tags:")
    print("-" * 80)
    projects_with_tags = [p for p in projects if p.tags]
    
    if not projects_with_tags:
        print("⚠️  No projects have tags!")
        print()
        print("Add tags to projects using:")
        print("  /edit_project <name> tags mobile,android,мобильный")
        print()
        return
    
    for project in projects_with_tags:
        print(f"  • {project.name}")
        print(f"    Tags: {', '.join(project.tags)}")
        print()
    
    # Initialize ProjectMatcher
    print("🔍 Initializing ProjectMatcher...")
    matcher = ProjectMatcher(threshold=0.5)
    print("✅ ProjectMatcher ready")
    print()
    
    # Test queries
    test_queries = [
        "мобильное приложение",
        "android app",
        "собрать флаттер проект",
        "ios приложение",
        "веб сайт",
        "desktop application"
    ]
    
    print("=" * 80)
    print("TESTING SEMANTIC SEARCH")
    print("=" * 80)
    print()
    
    for query in test_queries:
        print(f"🔎 Query: '{query}'")
        print("-" * 80)
        
        # Find all matching projects
        matches = matcher.find_projects_by_semantic_match(query, projects)
        
        if matches:
            print(f"✅ Found {len(matches)} match(es):")
            for project, score in matches:
                print(f"  • {project.name} (score: {score:.3f})")
                print(f"    Tags: {', '.join(project.tags)}")
        else:
            print("❌ No matches found")
        
        print()
    
    # Test find_best_project
    print("=" * 80)
    print("TESTING FIND BEST PROJECT")
    print("=" * 80)
    print()
    
    test_query = "мобильный проект"
    print(f"🔎 Query: '{test_query}'")
    print("-" * 80)
    
    best_match = matcher.find_best_project(test_query, projects)
    
    if best_match:
        project, score = best_match
        print(f"✅ Best match: {project.name} (score: {score:.3f})")
        print(f"   Tags: {', '.join(project.tags)}")
    else:
        print("❌ No match found")
    
    print()
    
    # Test find_project_by_name_or_tags
    print("=" * 80)
    print("TESTING UNIVERSAL SEARCH (NAME OR TAGS)")
    print("=" * 80)
    print()
    
    test_queries_universal = [
        projects[0].name if projects else "TestApp",  # Exact name
        "мобильное",  # By tags
        "app"  # Partial name
    ]
    
    for query in test_queries_universal:
        print(f"🔎 Query: '{query}'")
        print("-" * 80)
        
        project = matcher.find_project_by_name_or_tags(query, projects)
        
        if project:
            print(f"✅ Found: {project.name}")
            if project.tags:
                print(f"   Tags: {', '.join(project.tags)}")
        else:
            print("❌ Not found")
        
        print()
    
    print("=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

