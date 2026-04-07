"""
Models Package Initiallization
"""

from app.models.user import User
from app.models.group import Group, GroupMember

# This list helps Alembic discover all models
__all__ = [
    "User",
    "Group",
    "GroupMember",
]
