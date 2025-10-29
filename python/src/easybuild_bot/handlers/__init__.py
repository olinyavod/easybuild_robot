"""
Handlers package for bot conversation flows.
"""

from .add_project_wizard import AddProjectWizard, WAITING_NAME, WAITING_TYPE, WAITING_GIT_URL, WAITING_PROJECT_FILE_PATH, WAITING_DEV_BRANCH, WAITING_RELEASE_BRANCH, CONFIRM
from .edit_project_wizard import EditProjectWizard, SELECT_PROJECT, SELECT_FIELD, EDIT_VALUE

# For convenience, rename CONFIRM from add wizard to avoid conflicts
ADD_PROJECT_CONFIRM = CONFIRM
EDIT_PROJECT_CONFIRM = CONFIRM

__all__ = [
    'AddProjectWizard',
    'WAITING_NAME',
    'WAITING_TYPE', 
    'WAITING_GIT_URL',
    'WAITING_PROJECT_FILE_PATH',
    'WAITING_DEV_BRANCH',
    'WAITING_RELEASE_BRANCH',
    'ADD_PROJECT_CONFIRM',
    'EditProjectWizard',
    'SELECT_PROJECT',
    'SELECT_FIELD',
    'EDIT_VALUE',
    'EDIT_PROJECT_CONFIRM',
]

