"""Centralized administration and role changes."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditLog, User
from app.domain.admin import Capability, UserRole, has_capability


class PermissionDenied(PermissionError):
    """Actor lacks the required capability."""


class AdminService:
    """Keep role checks and auditable administrative writes in one service."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def change_role(self, *, actor_id: UUID, target_id: UUID, role: UserRole) -> User:
        actor = await self._session.scalar(select(User).where(User.id == actor_id))
        target = await self._session.scalar(select(User).where(User.id == target_id))
        if (
            actor is None
            or target is None
            or not has_capability(actor.role, Capability.CHANGE_ROLES)
        ):
            raise PermissionDenied("actor cannot change user roles")
        if actor.role != UserRole.SUPERADMIN and role in {UserRole.ADMIN, UserRole.SUPERADMIN}:
            raise PermissionDenied("only superadmin can grant administrative roles")
        old_role = target.role
        target.role = role
        self._session.add(
            AuditLog(
                actor_user_id=actor.id,
                action="role_changed",
                entity_type="user",
                entity_id=str(target.id),
                data={"from": old_role.value, "to": role.value},
                occurred_at=datetime.now(UTC),
            )
        )
        await self._session.commit()
        return target
