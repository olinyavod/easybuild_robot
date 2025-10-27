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

Creates a new project in the system using an **interactive step-by-step wizard**.

**Access**: Administrators only

**Format**:
```
/add_project
```

**Description**:
The bot will guide you through a step-by-step process to create a new project. You will be asked for:

1. **Project name** - Unique project name
2. **Project type** - Choose from Flutter, .NET MAUI, or Xamarin (interactive buttons)
3. **Git URL** - Git repository URL
4. **Project file path** - Path to project file relative to repository root
5. **Local path** - Local repository path on server
6. **Dev branch** - Development branch (default: `develop`, use `/skip` for default)
7. **Release branch** - Release branch (default: `main`, use `/skip` for default)
8. **Confirmation** - Review and confirm all details before creation

At any point, you can cancel the process by typing `/cancel`.

**Interactive Example**:
```
User: /add_project
Bot:  📝 Шаг 1 из 7: Название проекта
      Введите уникальное название для вашего проекта.

User: MyFlutterApp
Bot:  📦 Шаг 2 из 7: Тип проекта
      [Buttons: 🦋 Flutter | 🔷 .NET MAUI | 🔶 Xamarin]

User: [Clicks Flutter]
Bot:  🔗 Шаг 3 из 7: Git URL
      Введите URL Git-репозитория проекта.

User: https://github.com/user/myapp.git
...
```

For detailed documentation, see [ADD_PROJECT_WIZARD.md](ADD_PROJECT_WIZARD.md).

**Semantic tags**:
- "add project"
- "create project"
- "new project"
- "adding project"

---

### `/edit_project` - Edit Project

Edits settings of an existing project using an **interactive field selection menu**.

**Access**: Administrators only

**Format**:
```
/edit_project [project_name]
```

**Description**:
The bot will show an interactive menu with all project fields and their current values. You can:
1. Select project (if name not provided)
2. Choose field to edit from the menu
3. Enter new value
4. Edit multiple fields
5. Save all changes at once

**Interactive Example**:
```
User: /edit_project MyApp

Bot:  ✏️ Редактирование проекта
      
      🦋 Проект: MyApp
      📦 Тип: flutter
      
      Текущие значения:
      ✏️ Название проекта: MyApp
      📝 Описание: Мое приложение
      🔗 Git URL: https://github.com/user/myapp.git
      📁 Путь к файлу проекта: android/app
      🌿 Ветка разработки: develop
      🚀 Ветка релиза: main
      🏷️ Теги: mobile, android
      👥 Группы: все группы
      
      [Buttons for each field]
      [✅ Сохранить и выйти]
      [❌ Отменить]

User: [Clicks "✏️ Название проекта"]

Bot:  ✏️ Редактирование поля
      Поле: ✏️ Название проекта
      Текущее значение: MyApp
      
      💡 Введите новое значение...

User: MyAwesomeApp

Bot:  ✅ Значение сохранено!
      [Returns to field menu]

User: [Clicks "📝 Описание"]

Bot:  ✏️ Редактирование поля
      Поле: 📝 Описание проекта
      Текущее значение: Мое приложение
      
      💡 Введите новое значение...

User: Обновленное приложение v2

Bot:  ✅ Значение сохранено!
      [Returns to field menu]

User: [Clicks "✅ Сохранить и выйти"]

Bot:  ✅ Проект MyApp обновлен!
```

**Available fields for editing:**
- `name` - Project name (must be unique)
- `description` - Project description
- `git_url` - Git repository URL
- `project_file_path` - Project file path
- `dev_branch` - Development branch
- `release_branch` - Release branch
- `tags` - Tags (comma-separated)
- `groups` - Group IDs (comma-separated, empty = all groups)

> ℹ️ **Note:** The `local_repo_path` field is system-managed and cannot be edited manually.

**Special commands:**
- `/back` - Return to field menu (during value input)
- `/cancel` - Cancel editing (changes not saved)

For detailed documentation, see [EDIT_PROJECT_WIZARD.md](EDIT_PROJECT_WIZARD.md).

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

### Scenario 2: Renaming a Project

```bash
# Using interactive wizard
/edit_project OldAppName
# Select "✏️ Название проекта"
# Enter: NewAppName
# Click "✅ Сохранить и выйти"

# Or using command format
/edit_project OldAppName name NewAppName
```

### Scenario 3: Managing Project Access

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
