"""Roles and centralized administrative capabilities."""

from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class Capability(StrEnum):
    VIEW_ADMIN = "view_admin"
    MANAGE_USERS = "manage_users"
    CHANGE_ROLES = "change_roles"
    ADJUST_BANKROLL = "adjust_bankroll"
    EDIT_CONFIGURATION = "edit_configuration"


ROLE_CAPABILITIES: dict[UserRole, frozenset[Capability]] = {
    UserRole.USER: frozenset(),
    UserRole.MODERATOR: frozenset({Capability.VIEW_ADMIN, Capability.MANAGE_USERS}),
    UserRole.ADMIN: frozenset(
        {
            Capability.VIEW_ADMIN,
            Capability.MANAGE_USERS,
            Capability.ADJUST_BANKROLL,
            Capability.EDIT_CONFIGURATION,
        }
    ),
    UserRole.SUPERADMIN: frozenset(Capability),
}


def has_capability(role: UserRole, capability: Capability) -> bool:
    """Return whether a role is allowed to perform a capability."""

    return capability in ROLE_CAPABILITIES[role]
