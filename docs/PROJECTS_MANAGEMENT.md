# Project Management in EasyBuild Bot

## Overview

The project management system allows administrators to manage projects for building mobile applications. Projects can be of type Flutter, .NET MAUI, or Xamarin.

## Project Data Model

Each project contains the following information:

- **ID**: Unique project identifier (auto-generated)
- **Name**: Project name
- **Project Type**: Flutter, .NET MAUI, or Xamarin
- **Git URL**: Git repository URL
- **Project File Path**: Relative path from repository root
- **Local Repository Path**: Where the repository folder is stored on the server
- **Development Branch**: Git branch for development (default: `develop`)
- **Release Branch**: Git branch for releases (default: `main`)
- **Group List**: Telegram group IDs where the project is available (empty = all groups)
- **Tags**: Tags for matching with text command parameters
- **Description**: Optional project description

## Commands

### `/projects` - Project List

Shows list of available projects.

**Access**: All users

**Behavior**:
- In groups: shows only projects available for that group
- In private messages: shows all projects
- Administrators see additional information (ID, number of groups)

**Example**:
```
/projects
```

**Semantic tags**:
- "projects"
- "project list"
- "show projects"
- "what projects"
- "available projects"

---

### `/add_project` - Add Project

Creates a new project in the system.

**Access**: Administrators only

**Format**:
```
/add_project <name> <type> <git_url> <project_file_path> <local_path> [dev_branch] [release_branch]
```

**Parameters**:
- `name` - Project name (must be unique)
- `type` - Project type: `flutter`, `dotnet_maui` (or `maui`), `xamarin`
- `git_url` - Git repository URL
- `project_file_path` - Project file path relative to repository root
- `local_path` - Local repository path on server
- `dev_branch` - (Optional) Development branch (default: `develop`)
- `release_branch` - (Optional) Release branch (default: `main`)

**Examples**:
```bash
# Flutter project with default branches
/add_project MyFlutterApp flutter https://github.com/user/myapp.git android/app /home/repos/myapp

# .NET MAUI project with custom branches
/add_project MyMauiApp dotnet_maui https://github.com/user/mauiapp.git src/MyApp /home/repos/mauiapp dev master

# Xamarin project
/add_project MyXamarinApp xamarin https://github.com/user/xamarinapp.git Droid /home/repos/xamarinapp feature/v2 release/v2
```

**Semantic tags**:
- "add project"
- "create project"
- "new project"
- "adding project"

---

### `/edit_project` - Edit Project

Modifies settings of an existing project.

**Access**: Administrators only

**Format**:
```
/edit_project <name> <field> <value>
```

**Available fields**:
- `description` - Project description
- `dev_branch` - Development branch
- `release_branch` - Release branch
- `tags` - Tags (comma-separated)
- `groups` - Group IDs (comma-separated, empty = all groups)
- `git_url` - Git repository URL
- `project_file_path` - Project file path
- `local_repo_path` - Local repository path

**Examples**:
```bash
# Add description
/edit_project MyApp description My Android application

# Set tags
/edit_project MyApp tags mobile,android,production

# Restrict access to specific groups
/edit_project MyApp groups -1001234567890,-1009876543210

# Allow access for all groups (empty value)
/edit_project MyApp groups 

# Change development branch
/edit_project MyApp dev_branch feature/new-ui

# Change Git URL
/edit_project MyApp git_url https://github.com/newuser/myapp.git
```

**Semantic tags**:
- "edit project"
- "modify project"
- "configure project"
- "update project"

---

### `/delete_project` - Delete Project

Deletes a project from the system.

**Access**: Administrators only

**Format**:
```
/delete_project <name>
```

**Parameters**:
- `name` - Name of project to delete

**Example**:
```
/delete_project MyOldApp
```

⚠️ **Warning**: This action cannot be undone!

**Semantic tags**:
- "delete project"
- "remove project"
- "erase project"
- "drop project"

---

## Usage Examples

### Scenario 1: Creating a New Flutter Project

```bash
# 1. Create project
/add_project ChecklistApp flutter https://github.com/company/checklist.git android/app /home/repos/checklist

# 2. Add description
/edit_project ChecklistApp description Production checklist application

# 3. Add search tags
/edit_project ChecklistApp tags checklist,production,mobile

# 4. Restrict access to work group only
/edit_project ChecklistApp groups -1001234567890
```

### Scenario 2: Managing Project Access

```bash
# Show all projects (admin)
/projects

# Restrict project to two groups
/edit_project ProjectA groups -1001111111,-1002222222

# Make project available to all groups
/edit_project ProjectA groups 

# View projects in specific group
# (execute command in the group)
/projects
```

### Scenario 3: Updating Project Configuration

```bash
# Change development branch
/edit_project MyApp dev_branch feature/v2

# Change release branch
/edit_project MyApp release_branch release/v2

# Update repository path
/edit_project MyApp local_repo_path /var/repos/myapp
```

## Technical Details

### Data Storage

Projects are stored in the `projects` collection of the MontyDB database with the following structure:

```python
{
    "id": "uuid-string",
    "name": "ProjectName",
    "project_type": "flutter|dotnet_maui|xamarin",
    "git_url": "https://github.com/...",
    "project_file_path": "path/to/project",
    "local_repo_path": "/home/repos/project",
    "dev_branch": "develop",
    "release_branch": "main",
    "allowed_group_ids": [list of int],
    "tags": [list of str],
    "description": "Optional description"
}
```

### Indexes

- `id` - unique index
- `name` - regular index for fast name lookup

### Storage API Methods

#### CRUD Operations

- `add_project(project: Project)` - Add or update project
- `get_project_by_id(project_id: str)` - Get project by ID
- `get_project_by_name(name: str)` - Get project by name (case-insensitive)
- `get_all_projects()` - Get all projects
- `delete_project(project_id: str)` - Delete project

#### Special Queries

- `find_projects_by_tag(tag: str)` - Find projects by tag
- `get_projects_for_group(group_id: int)` - Get projects for specific group
- `update_project_groups(project_id: str, group_ids: List[int])` - Update group list
- `update_project_tags(project_id: str, tags: List[str])` - Update tags

### Command Pattern Integration

All project management commands are implemented using the Command Pattern:

- `ProjectsCommand` - View project list
- `AddProjectCommand` - Add project
- `EditProjectCommand` - Edit project
- `DeleteProjectCommand` - Delete project

Commands are automatically registered in `CommandRegistry` through `create_command_system()` in `factory.py`.

## Security

- Commands `/add_project`, `/edit_project`, `/delete_project` are available to administrators only
- Command `/projects` is available to all users with bot access
- In groups, only projects allowed for that group are shown
- Empty `allowed_group_ids` list means the project is available in all groups

## Future Improvements

- [ ] Command for bulk importing projects from JSON/YAML file
- [ ] Export project configuration
- [ ] Project change history
- [ ] Path and Git URL validation
- [ ] Automatic repository availability checking
- [ ] Integration with build system
- [ ] Roles and permissions at project level
