from app.domain.admin import Capability, UserRole, has_capability


def test_capabilities_are_centralized_by_role() -> None:
    assert not has_capability(UserRole.USER, Capability.VIEW_ADMIN)
    assert has_capability(UserRole.ADMIN, Capability.ADJUST_BANKROLL)
    assert has_capability(UserRole.SUPERADMIN, Capability.CHANGE_ROLES)


def test_all_roles_exist() -> None:
    assert {role.value for role in UserRole} == {"user", "moderator", "admin", "superadmin"}
